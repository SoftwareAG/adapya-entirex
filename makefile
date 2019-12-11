#
#   make file
#
#   %make% VRL=0.9.4 WC=NO all
#   %make% VRL=0.9.4 WC=YES all    (take from working copy not from committed version in SVN)

#.SILENT: clean env nose-cover test-cover qa test doc release upload
.PHONY: clean release docs

#VERSION=2.7
#PYPI=http://pypi.python.org/simple
#DIST_DIR=dist

PYTHON=python
SED=C:\BAT\UnxUtils\upd\sed
THISYEAR=2019
SUBP=entirex        # subpackage
PACK=adapya-$(SUBP) # adapya package
MAKDIR=C:\temp\apy

#EASY_INSTALL=env/bin/easy_install-$(VERSION)
#PYTEST=env/bin/py.test-$(VERSION)
#NOSE=env/bin/nosetests-$(VERSION
APYURL=http://redsvngis.eur.ad.sag/ADA/adapy
APYWC=C:\adas\adapy
GITDIR=C:\adas\git

SVN="C:\Program Files\TortoiseSVN\bin\svn.exe"
SVNVERSION="C:\Program Files\TortoiseSVN\bin\svnversion.exe"


# VRL version.release.level (e.g. 1.2.3) must be set from outside
!IF "$(VRL)" == ""
!ERROR Input define VRL for makefile missing
!ENDIF

# WC=YES take working copy otherwise from repository (new members must be committed in SVN)
!IF "$(WC)" == "YES"
APYURL=$(APYWC)
!ENDIF


all: clean release docs

info:
    $(SVN) info  . $(APYURL)/trunk
    $(SVNVERSION)


clean:
    cd C:/temp/apy
    -rd $(PACK)-$(VRL) /s /q
    del $(PACK)-$(VRL).*

#        find src/ -type d -name __pycache__ | xargs rm -rf
#        find src/ -name '*.py[co]' -delete
#        find src/ -name '*.so' -delete
#        rm -rf dist/ build/ doc/_build/ MANIFEST src/*.egg-info .cache .coverage

release:
    cd $(MAKDIR)
    $(SVN) export $(APYURL)/trunk/adapya-entirex $(PACK)-$(VRL) --depth=files
    $(SVN) export $(APYURL)/trunk/adapya $(PACK)-$(VRL)/adapya --depth=files
    $(SVN) export $(APYURL)/trunk/adapya/entirex $(PACK)-$(VRL)/adapya/entirex
    $(SVN) export $(APYURL)/trunk/adapya-entirex/doc/source $(PACK)-$(VRL)/adapya/entirex/doc
    cd $(PACK)-$(VRL)
    $(SED) -i "s/v.r.l/$(VRL)/" setup.py adapya\entirex\*.py adapya\entirex\doc\*.py adapya\entirex\doc\*.rst
    $(SED) -i "s/ThisYear/$(THISYEAR)/" adapya\entirex\*.py adapya\entirex\doc\*.py adapya\entirex\doc\*.rst
    rem --- delete  GIT directory mirror but leave hidden files (.git)
    del /A-H /q $(GITDIR)\$(PACK)\*.*
    rem del /S /q $(GITDIR)\$(PACK)\adapya\*.*
    xcopy /s /y /q * $(GITDIR)\$(PACK)
    rem # cd $(GITDIR)\$(PACK)
    rem # pandoc --from=rst --to=gfm --output=README.md README.rst
    rem # cd $(MAKDIR)/$(PACK)-$(VRL)
    rem ---
    $(PYTHON) setup.py sdist --formats=tar,zip
    cd ..
    xcopy $(PACK)-$(VRL)\dist\* ..\apy

tag:
    $(SVN) copy $(APYURL)/trunk/adapya-entirex \
         $(APYURL)/tags/adapya-entirex-$(VRL)\
         -m "Tagging the $(VRL) release of the 'adapya-entirex' project."

# XCOPY /D copies files only newer than target /S include subdir /Y no prompt

upload:
    cd C:/temp/apy
    xcopy /D /Y $(PACK)-$(VRL).* V:\tools\Python\adapya
    cd C:$(PACK)-$(VRL)/adapya/$(SUBP)
    xcopy /S /D /Y doc\_build V:\tools\Python\adapya\doc\$(SUBP)


# sphinx-build option -a always write all output files
# copy .nojekyll file to docs dir: this will disable GIGHUB's own pages formatting

docs:
    cd C:/temp/apy/$(PACK)-$(VRL)/adapya/entirex
    sphinx-build -a doc/ doc/_build/
    xcopy /D $(APYWC)\trunk\*.nojekyll $(GITDIR)\$(PACK)\docs
    xcopy /D /s /y /q doc\_build\* $(GITDIR)\$(PACK)\docs


