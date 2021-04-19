# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme

from mock import Mock as MagicMock
from sphinx.builders.html import (
    StandaloneHTMLBuilder,
    DirectoryHTMLBuilder,
    SingleFileHTMLBuilder,
)

sys.path.insert(0, os.path.abspath("../gospl/"))

# Redefine supported_image_types for the HTML builder
html_img_types = ["image/gif", "image/svg+xml", "image/png", "image/jpeg"]
StandaloneHTMLBuilder.supported_image_types = html_img_types
DirectoryHTMLBuilder.supported_image_types = html_img_types
SingleFileHTMLBuilder.supported_image_types = html_img_types


# -- Project information -----------------------------------------------------

project = "gospl"
copyright = "2020-2024, EarthCodeLab Group"
author = "Tristan Salles"

# version = '%s r%s' % (pandas.__version__, svn_version())
# version = str(gospl.__version__)
# The full version, including alpha/beta/rc tags.
# release = version

# The short X.Y version
version = "0.2.4"
# The full version, including alpha/beta/rc tags
release = "0.2.4"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.todo",
    "sphinxcontrib.napoleon",
    "sphinx.ext.autodoc",
    "sphinxemoji.sphinxemoji",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.linkcode",
    "nbsphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    # "numpydoc",
    "myst_parser",
    "sphinxcontrib.bibtex",
]
bibtex_bibfiles = ["refs.bib"]

# nbsphinx do not use requirejs (breaks bootstrap)
nbsphinx_requirejs_path = ""

numfig = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
# pygments_style = "monokai"
# pygments_style = "default"
sphinxemoji_style = "twemoji"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "classic"
# html_theme = "sphinx_rtd_theme"
html_theme = "pydata_sphinx_theme"

# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_logo = "images/logo.png"
html_theme_options = {
    "github_url": "https://github.com/Geodels/gospl",
    "search_bar_text": "Search GOSPL docs ...",
}
# html_theme_options = {
#     "logo_only": True,
#     "display_version": False,
# }


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/getting_started.css",
    "css/gospl.css",
]

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "images/favicon.ico"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["nstatic"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "gospldoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "gospl.tex", "gospl Documentation", "Tristan Salles", "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "gospl", "gospl Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "gospl",
        "gospl Documentation",
        author,
        "gospl",
        "Global Landscape Evolution Model.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Mock utils
# utils contains binary (FORTRAN and C) code for the performance-sensitive
# parts of Badlands. readthedocs can't compile or load this, so we mock it
# out.
# See also http://docs.readthedocs.io/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = [
    "h5py",
    "mpi4py",
    "Cython",
    "ruamel",
    "ruamel.yaml",
    "pandas",
    "scipy",
    "petsc4py",
    "meshplex",
    "scipy.interpolate",
    "vtk",
    "vtk.util",
]

for m in MOCK_MODULES:
    sys.modules[m] = Mock()


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)


# Generate the API documentation when building
autosummary_generate = True
autosummary_imported_members = True
numpydoc_show_class_members = True
class_members_toctree = True
numpydoc_show_inherited_class_members = True
numpydoc_use_plots = True
myst_update_mathjax = False


nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. note::

        | This page was generated from `{{ docname }}`__.
        | The binder version is quite slow due to memory and CPUs limitations
        | accordingly provided examples have been slightly simplified...
        | Interactive online version: :raw-html:`<a href="https://mybinder.org/v2/gh/Geodels/gospl/binder?urlpath=tree/{{ docname }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

        __ https://github.com/Geodels/gospl/blob/master/docs/{{ docname }}
"""
# nbsphinx_prolog = r"""
# """


def linkcode_resolve(domain, info):
    def find_source():
        # try to find the file and line number, based on code from numpy:
        # https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L286
        obj = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)
        import inspect
        import os

        fn = inspect.getsourcefile(obj)
        filepath = os.path.dirname(__file__)
        relpath = "/".join(filepath.split("/")[:-1]) + "/gospl"
        fn = os.path.relpath(fn, start=relpath)
        source, lineno = inspect.getsourcelines(obj)

        return fn, lineno, lineno + len(source) - 1

    if domain != "py" or not info["module"]:
        return None
    try:
        filename = "%s#L%d-L%d" % find_source()
    except Exception:
        filename = info["module"].replace(".", "/") + ".py"
    tag = "master" if "+" in release else ("v" + release)
    tag = "master"

    return "https://github.com/Geodels/gospl/blob/%s/gospl/%s" % (tag, filename)
