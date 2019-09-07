import gc
import numpy as np
from mpi4py import MPI
from scipy import sparse

import sys,petsc4py
petsc4py.init(sys.argv)
from petsc4py import PETSc
from time import clock

from gLEM._fortran import fillPIT
from gLEM._fortran import MFDreceivers
from gLEM._fortran import setHillslopeCoeff

MPIrank = PETSc.COMM_WORLD.Get_rank()
MPIsize = PETSc.COMM_WORLD.Get_size()
MPIcomm = PETSc.COMM_WORLD

try: range = xrange
except: pass

class SPMesh(object):
    """
    Building the surface processes based on different neighbour conditions
    """
    def __init__(self, *args, **kwargs):

        # KSP solver parameters
        self.rtol = 1.0e-8

        # Identity matrix construction
        self.iMat = self._matrix_build_diag(np.ones(self.npoints))

        # Petsc vectors
        self.FillG = self.hGlobal.duplicate()
        self.FillL = self.hLocal.duplicate()
        self.FAG = self.hGlobal.duplicate()
        self.FAL = self.hLocal.duplicate()
        self.hOld = self.hGlobal.duplicate()
        self.hOldLocal = self.hLocal.duplicate()
        self.stepED = self.hGlobal.duplicate()
        self.tmpL = self.hLocal.duplicate()
        self.vGlob = self.hGlobal.duplicate()
        self.Eb = self.hGlobal.duplicate()
        self.EbLocal = self.hLocal.duplicate()
        self.vSed = self.hGlobal.duplicate()
        self.vSedLocal = self.hLocal.duplicate()

        # Diffusion matrix construction
        if self.Cd > 0.:
            diffCoeffs, maxnb = setHillslopeCoeff(self.npoints,self.Cd*self.dt)
            self.Diff = self._matrix_build_diag(diffCoeffs[:,0])

            for k in range(0,maxnb):
                tmpMat = self._matrix_build()
                indptr = np.arange(0, self.npoints+1, dtype=PETSc.IntType)
                indices = self.FVmesh_ngbID[:,k].copy()
                data = np.zeros(self.npoints)
                ids = np.nonzero(indices<0)
                indices[ids] = ids
                data = diffCoeffs[:,k+1]
                ids = np.nonzero(data==0.)
                indices[ids] = ids
                tmpMat.assemblyBegin()
                tmpMat.setValuesLocalCSR(indptr, indices.astype(PETSc.IntType), data,
                                         PETSc.InsertMode.INSERT_VALUES)
                tmpMat.assemblyEnd()
                self.Diff += tmpMat
                tmpMat.destroy()
            del ids, indices, indptr
            gc.collect()

        return

    def _matrix_build(self, nnz=(1,1)):
        """
        Define PETSC Matrix
        """

        matrix = PETSc.Mat().create(comm=MPIcomm)
        matrix.setType('aij')
        matrix.setSizes(self.sizes)
        matrix.setLGMap(self.lgmap_row, self.lgmap_col)
        matrix.setFromOptions()
        matrix.setPreallocationNNZ(nnz)

        return matrix

    def _matrix_build_diag(self, V, nnz=(1,1)):
        """
        Define PETSC Diagonal Matrix
        """

        matrix = self._matrix_build()

        # Define diagonal matrix
        I = np.arange(0, self.npoints+1, dtype=PETSc.IntType)
        J = np.arange(0, self.npoints, dtype=PETSc.IntType)
        matrix.assemblyBegin()
        matrix.setValuesLocalCSR(I, J, V, PETSc.InsertMode.INSERT_VALUES)
        matrix.assemblyEnd()
        del I, J

        return matrix

    def _make_reasons(self,reasons):
        return dict([(getattr(reasons, r), r)
             for r in dir(reasons) if not r.startswith('_')])

    def _solve_KSP(self, guess, matrix, vector1, vector2):
        """
        Set PETSC KSP solver.

        Args
            guess: Boolean specifying if the iterative KSP solver initial guess is nonzero
            matrix: PETSC matrix used by the KSP solver
            vector1: PETSC vector corresponding to the initial values
            vector2: PETSC vector corresponding to the new values

        Returns:
            vector2: PETSC vector of the new values
        """

        ksp = PETSc.KSP().create(PETSc.COMM_WORLD)
        if guess:
            ksp.setInitialGuessNonzero(guess)
        ksp.setOperators(matrix,matrix)
        ksp.setType('richardson')
        pc = ksp.getPC()
        pc.setType('bjacobi')
        ksp.setTolerances(rtol=self.rtol)
        ksp.solve(vector1, vector2)
        r = ksp.getConvergedReason()
        if r < 0:
            KSPReasons = self._make_reasons(PETSc.KSP.ConvergedReason())
            print('LinearSolver failed to converge after %d iterations',ksp.getIterationNumber())
            print('with reason: %s',KSPReasons[r])
            raise RuntimeError("LinearSolver failed to converge!")
        ksp.destroy()

        return vector2

    def _buildFlowDirection(self, h1):
        """
        Build multiple flow direction based on neighbouring slopes.
        """

        t0 = clock()

        # Account for marine regions
        self.seaID = np.where(h1<=self.sealevel)[0]

        # Define multiple flow directions
        self.rcvID, self.slpRcv, self.distRcv, self.wghtVal = MFDreceivers(self.flowDir, self.inIDs, h1)

        # Set depression nodes
        self.rcvID[self.seaID,:] = np.tile(self.seaID,(self.flowDir,1)).T
        self.distRcv[self.seaID,:] = 0.
        self.wghtVal[self.seaID,:] = 0.

        if MPIrank == 0 and self.verbose:
            print('Flow Direction declaration (%0.02f seconds)'% (clock() - t0))

        return

    def FlowAccumulation(self):
        """
        Compute multiple flow accumulation.
        """

        self.dm.globalToLocal(self.hGlobal, self.hLocal)
        # Get global elevation for pit filling...
        t0 = clock()
        hl = self.hLocal.getArray().copy()
        gZ = np.zeros(self.gpoints)
        gZ = hl[self.lgIDs]
        gZ[self.outIDs] = -1.e8
        MPI.COMM_WORLD.Allreduce(MPI.IN_PLACE, gZ, op=MPI.MAX)

        # Perform pit filling
        nZ = fillPIT(self.sealevel-500.,gZ)
        self._buildFlowDirection(nZ[self.glIDs])

        # Update fill elevation
        id = nZ<self.sealevel
        nZ[id] = gZ[id]
        self.pitID = np.where(nZ[self.glIDs]>hl)[0]
        self.FillL.setArray(nZ[self.glIDs])
        self.dm.localToGlobal(self.FillL, self.FillG)
        del hl, nZ, gZ, id
        if MPIrank == 0 and self.verbose:
            print('Compute pit filling (%0.02f seconds)'% (clock() - t0))

        t0 = clock()
        # Build drainage area matrix
        WAMat = self.iMat.copy()
        for k in range(0, self.flowDir):
            tmpMat = self._matrix_build()
            data = -self.wghtVal[:,k].copy()
            indptr = np.arange(0, self.npoints+1, dtype=PETSc.IntType)
            nodes = indptr[:-1]
            data[self.rcvID[:,k].astype(PETSc.IntType)==nodes] = 0.0
            tmpMat.assemblyBegin()
            tmpMat.setValuesLocalCSR(indptr, self.rcvID[:,k].astype(PETSc.IntType),
                                     data, PETSc.InsertMode.INSERT_VALUES)
            tmpMat.assemblyEnd()
            WAMat += tmpMat
            tmpMat.destroy()
        del data, indptr

        # Solve flow accumulation
        WAtrans = WAMat.transpose()
        self.WeightMat = WAtrans.copy()
        if self.tNow == self.tStart:
            self._solve_KSP(False, self.WeightMat, self.bG, self.FAG)
        else:
            self._solve_KSP(True, self.WeightMat, self.bG, self.FAG)
        WAMat.destroy()
        WAtrans.destroy()

        self.dm.globalToLocal(self.FAG, self.FAL, 1)
        gc.collect()

        if MPIrank == 0 and self.verbose:
            print('Compute Flow Accumulation (%0.02f seconds)'% (clock() - t0))

        return

    def _getErosionRate(self):
        """
        Compute sediment and bedrock erosion rates.
        """

        Kcoeff = self.FAL.getArray()
        Kbr = np.sqrt(Kcoeff)*self.K*self.dt
        Kbr[self.seaID] = 0.
        Kbr[self.pitID] = 0.

        # Initialise identity matrices...
        EbedMat = self.iMat.copy()
        wght = self.wghtVal.copy()

        # Define erosion coefficients
        for k in range(0, self.flowDir):

            indptr = np.arange(0, self.npoints+1, dtype=PETSc.IntType)
            nodes = indptr[:-1]
            # Define erosion limiter to prevent formation of flat
            dh = self.hOldArray-self.hOldArray[self.rcvID[:,k]]
            limiter = np.divide(dh, dh+1.e-3, out=np.zeros_like(dh), where=dh!=0)

            # Bedrock erosion processes SPL computation (maximum bedrock incision)
            data = np.divide(Kbr*limiter, self.distRcv[:,k], out=np.zeros_like(Kcoeff),
                                        where=self.distRcv[:,k]!=0)
            tmpMat = self._matrix_build()
            wght[self.seaID,k] = 0.
            data = np.multiply(data,-wght[:,k])
            data[self.rcvID[:,k].astype(PETSc.IntType)==nodes] = 0.0
            tmpMat.assemblyBegin()
            tmpMat.setValuesLocalCSR(indptr, self.rcvID[:,k].astype(PETSc.IntType),
                                     data, PETSc.InsertMode.INSERT_VALUES)
            tmpMat.assemblyEnd()
            EbedMat += tmpMat
            Mdiag = self._matrix_build_diag(data)
            EbedMat -= Mdiag
            tmpMat.destroy()
            Mdiag.destroy()
            del data
        del dh, limiter, wght

        # Solve bedrock erosion thickness
        self._solve_KSP(True, EbedMat, self.hOld, self.vGlob)
        EbedMat.destroy()
        self.stepED.waxpy(-1.0,self.hOld,self.vGlob)

        # Define erosion rate (positive for incision)
        E = -self.stepED.getArray().copy()
        E = np.divide(E,self.dt)
        E[E<0.] = 0.
        self.Eb.setArray(E)
        self.dm.globalToLocal(self.Eb, self.EbLocal, 1)
        E = self.EbLocal.getArray().copy()
        E[self.seaID] = 0.
        E[self.pitID] = 0.
        self.EbLocal.setArray(E)
        self.dm.localToGlobal(self.EbLocal, self.Eb, 1)
        del E, Kcoeff, Kbr

        return

    def cptErosion(self):
        """
        Compute erosion using stream power law.
        """

        t0 = clock()

        # Constant local & global vectors/arrays
        self.Eb.set(0.)
        self.hGlobal.copy(result=self.hOld)
        self.dm.globalToLocal(self.hOld, self.hOldLocal, 1)
        self.hOldArray = self.hOldLocal.getArray().copy()
        self._getErosionRate()

        # Update bedrock thicknesses due to erosion
        Eb = self.Eb.getArray().copy()
        self.stepED.setArray(-Eb*self.dt)
        self.cumED.axpy(1.,self.stepED)
        self.dm.globalToLocal(self.cumED, self.cumEDLocal, 1)

        self.hGlobal.axpy(1.,self.stepED)
        self.dm.globalToLocal(self.hGlobal, self.hLocal, 1)
        del Eb
        gc.collect()

        if MPIrank == 0 and self.verbose:
            print('Get Erosion Thicknesses (%0.02f seconds)'% (clock() - t0))

        return

    def cptSedFlux(self):
        """
        Compute sediment flux.
        """

        # Build sediment load matrix
        t0 = clock()
        SLMat = self.WeightMat.copy()
        SLMat -= self.iMat
        SLMat.scale(1.-self.wgth)
        SLMat += self.iMat
        Eb = self.Eb.getArray().copy()
        Eb = np.multiply(Eb,1.0-self.frac_fine)
        self.stepED.setArray(Eb)
        self.stepED.pointwiseMult(self.stepED,self.areaGlobal)
        if self.tNow == self.tStart:
            self._solve_KSP(False, SLMat, self.stepED, self.vSed)
        else :
            self._solve_KSP(True, SLMat, self.stepED, self.vSed)
        SLMat.destroy()
        # Update local vector
        self.dm.globalToLocal(self.vSed, self.vSedLocal, 1)
        if MPIrank == 0 and self.verbose:
            print('Update Sediment Load (%0.02f seconds)'% (clock() - t0))
        del Eb
        gc.collect()

        # Get deposition thickness
        if self.wgth == 0.:
            return
        t0 = clock()
        self.stepED.set(0.)
        self.stepED.axpy(-(1.0-self.frac_fine),self.Eb)
        self.stepED.pointwiseMult(self.stepED,self.areaGlobal)
        self.stepED.axpy(1.,self.vSed)
        self.stepED.scale(self.wgth*self.dt/(1.-self.wgth))
        self.stepED.pointwiseDivide(self.stepED,self.areaGlobal)
        self.cumED.axpy(1.,self.stepED)
        self.dm.globalToLocal(self.cumED, self.cumEDLocal, 1)

        self.hGlobal.axpy(1.,self.stepED)
        self.dm.globalToLocal(self.hGlobal, self.hLocal, 1)
        if MPIrank == 0 and self.verbose:
            print('Get River Deposition (%0.02f seconds)'% (clock() - t0))

        return

    def HillSlope(self):
        """
        Perform hillslope diffusion.
        """

        t0 = clock()
        if self.Cd > 0.:
            # Get erosion values for considered time step
            self.hGlobal.copy(result=self.hOld)
            self._solve_KSP(True, self.Diff, self.hOld, self.hGlobal)

            # Update cumulative erosion/deposition and soil/bedrock elevation
            self.stepED.waxpy(-1.0,self.hOld,self.hGlobal)
            self.cumED.axpy(1.,self.stepED)
            self.dm.globalToLocal(self.cumED, self.cumEDLocal, 1)
            self.dm.globalToLocal(self.hGlobal, self.hLocal, 1)

        if MPIrank == 0 and self.verbose:
            print('Compute Hillslope Processes (%0.02f seconds)'% (clock() - t0))

        return


    def SedimentDiffusion(self):
        """
        Perform marine diffusion from freshly deposited sediments.
        """

        t0 = clock()

        # Get the marine volumetric sediment rate (m3/yr) to diffuse during the time step...
        tmp = self.vSedLocal.getArray().copy()
        depVol = np.zeros(self.npoints)
        depVol[self.seaID] = tmp[self.seaID]
        del tmp, depVol
        gc.collect()
        # self.sedimentK

        # self.tmp = self.vSed.duplicate()
        # self.tmpL = self.vSedLocal.duplicate()
        # self.tmp.scale(self.dt)
        # self.tmp.pointwiseDivide(self.tmp,self.areaGlobal)
        # self.dm.globalToLocal(self.tmp, self.tmpL, 1)
        # dh = self.tmpL.getArray().copy()
        # depo = np.zeros(self.npoints)
        # depo[self.seaID] = dh[self.seaID]
        # self.tmpL.setArray(depo)
        # self.dm.localToGlobal(self.tmpL, self.tmp)
        # self.cumED.axpy(1.,self.tmp)
        # self.dm.globalToLocal(self.cumED, self.cumEDLocal, 1)
        # self.hGlobal.axpy(1.,self.tmp)
        # self.dm.globalToLocal(self.hGlobal, self.hLocal, 1)
        # self.tmpL.destroy()
        # self.tmp.destroy()
        # if MPIrank == 0 and self.verbose:
        #     print('Fake Marine River Deposition (%0.02f seconds)'% (clock() - t0))


        if MPIrank == 0 and self.verbose:
            print('Compute Sediment Diffusion (%0.02f seconds)'% (clock() - t0))
