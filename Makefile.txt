# Compiler
CXX = g++

# Compiler flags
# unsolvable: -Wmissing-declarations -Wold-style-cast -Waggregate-return -Wimplicit -Weffc++ -Wpadded
# solved:
# 	-pedantic -pedantic-errors -Wextra  -Wcast-align \
# 	-Wcast-qual -Wconversion \
# 	-Wdisabled-optimization \
# 	-Werror -Wfloat-equal -Wformat=2 \
# 	-Wformat-nonliteral -Wformat-security  \
# 	-Wformat-y2k \
# 	  -Wimport  -Winit-self  -Winline \
# 	-Winvalid-pch   \
# 	-Wlong-long \
# 	-Wmissing-field-initializers -Wmissing-format-attribute   \
# 	-Wmissing-include-dirs -Wmissing-noreturn \
# 	-Wpacked   -Wpointer-arith \
# 	-Wredundant-decls \
# 	-Wshadow -Wstack-protector \
# 	-Wstrict-aliasing=2 -Wswitch-default \
# 	-Wswitch-enum \
# 	-Wunreachable-code -Wunused \
# 	-Wunused-parameter \
# 	-Wvariadic-macros \
# 	-Wwrite-strings
CXXFLAGS = -Wall -Wextra -std=c++11 -Ofast $(EXTRA_CXXFLAGS)	


# Include directories
INCLUDES = -I.

# Source files
SRCS = io.cpp Screen.cpp Player.cpp Ball.cpp main.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Executable name
GAME = game
GAME_EXE = ${GAME}

# AppImage directories
APPDIR=AppImageBuild
AppName=autotester
TESTER_FOLDER=/u/course/ece244i/public/2/common/tester
DOWNLOADED_STUFF_FOLDER = ${TESTER_FOLDER}/downloads
REF_OUTPUT_FOLDER = ${TESTER_FOLDER}/reference_solution_outputs

# Python script
PYTHON_SCRIPT_HELPER=tester.py
PYTHON_SCRIPT=tester_with_ece244i.py

# Default target
all: $(AppName)

# Linking
$(GAME_EXE): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $(GAME_EXE)

# Compiling
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@


#####################################
#python stuff

.pexpect-4.9.zip:
	wget -O .pexpect-4.9.zip https://github.com/pexpect/pexpect/archive/refs/tags/4.9.zip
	unzip .pexpect-4.9.zip

${APPDIR}/usr/bin/ptyprocess: #.pexpect-4.9.zip
	mkdir -p ${APPDIR}/usr/bin/ptyprocess
	cp $(DOWNLOADED_STUFF_FOLDER)/ptyprocess/* ${APPDIR}/usr/bin/ptyprocess

${APPDIR}/usr/bin/pexpect49: #.pexpect-4.9.zip
	mkdir -p ${APPDIR}/usr/bin/pexpect49
	cp $(DOWNLOADED_STUFF_FOLDER)/pexpect/* ${APPDIR}/usr/bin/pexpect49

${APPDIR}/usr/bin/reference_solution_outputs:
	mkdir -p ${APPDIR}/usr/bin/reference_solution_outputs
	cp -r $(REF_OUTPUT_FOLDER)/* ${APPDIR}/usr/bin/reference_solution_outputs/


#####################################
#app image stuff

nonecf:
	$(MAKE) TESTER_FOLDER=tester DOWNLOADED_STUFF_FOLDER=tester/downloads REF_OUTPUT_FOLDER=tester/reference_solution_outputs

$(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage:
	wget -O $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
	chmod +x $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage

${APPDIR}/usr/bin: ${TESTER_FOLDER}/$(PYTHON_SCRIPT) $(GAME_EXE) ${APPDIR}/usr/bin/pexpect49 ${APPDIR}/usr/bin/ptyprocess ${APPDIR}/usr/bin/reference_solution_outputs
	mkdir -p ${APPDIR}/usr/bin
	cp $(GAME_EXE) ${APPDIR}/usr/bin
	cp ${TESTER_FOLDER}/$(PYTHON_SCRIPT) ${APPDIR}/usr/bin
	cp ${TESTER_FOLDER}/$(PYTHON_SCRIPT_HELPER) ${APPDIR}/usr/bin
	chmod +x ${APPDIR}/usr/bin/$(GAME_EXE)
	chmod +x ${APPDIR}/usr/bin/$(PYTHON_SCRIPT)
	chmod +x ${APPDIR}/usr/bin/$(PYTHON_SCRIPT_HELPER)

${APPDIR}/app.png:
	cp $(DOWNLOADED_STUFF_FOLDER)/app.png ${APPDIR}/app.png
	# wget -O ${APPDIR}/app.png https://upload.wikimedia.org/wikipedia/commons/3/3e/Tree-256x256.png

${APPDIR}/${AppName}.desktop: ${APPDIR}/usr/bin 
	echo "[Desktop Entry]" > ${APPDIR}/${AppName}.desktop
	echo "Name=${AppName}" >> ${APPDIR}/${AppName}.desktop
	echo "Exec=doesNotMatterLol" >> ${APPDIR}/${AppName}.desktop
	echo "Icon=app" >> ${APPDIR}/${AppName}.desktop
	echo "Type=Application" >> ${APPDIR}/${AppName}.desktop
	echo "Categories=Utility;" >> ${APPDIR}/${AppName}.desktop

${APPDIR}/AppRun: ${APPDIR}/usr/bin
	echo "#!/bin/bash" > ${APPDIR}/AppRun
	echo "HERE=\$$(dirname \"\$$(readlink -f \"\$$0\")\")" >> ${APPDIR}/AppRun
	echo "exec python3.12 \"\$$HERE/usr/bin/$(PYTHON_SCRIPT)\" \"\$$@\"" >> ${APPDIR}/AppRun
	chmod +x ${APPDIR}/AppRun

${AppName}: EXTRA_CXXFLAGS=-DRUNNING_WITH_PYTHON_TESTER=1
${AppName}: $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage ${APPDIR}/usr/bin ${APPDIR}/app.png ${APPDIR}/${AppName}.desktop ${APPDIR}/AppRun
	if [ ! -x $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage ]; then \
		chmod +x $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage; \
	fi
	ARCH=x86_64 $(DOWNLOADED_STUFF_FOLDER)/appimagetool-x86_64.AppImage ${APPDIR}
	mv ${AppName}-x86_64.AppImage ${AppName}
	@echo "===========BUILD SUCCESS===========";
	@echo "Please use this command to run the autotester: ./${AppName}";
	
# Clean target
clean:
	rm -rf $(OBJS) $(GAME_EXE) ${APPDIR} ${AppName}

.PHONY: clean