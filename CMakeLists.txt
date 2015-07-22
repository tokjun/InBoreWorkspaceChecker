cmake_minimum_required(VERSION 2.8.9)

project(InBoreWorkspaceChecker)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/InBoreWorkspaceChecker")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "Junichi Tokuda (BWH)")
set(EXTENSION_DESCRIPTION "3D Slicer scripted module to estimate 3D ablation volume.")
set(EXTENSION_ICONURL "http://www.slicer.org/slicerWiki/images/b/b7/InBoreWorkspaceCheckerIcon.png")
set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/0/0b/Slicer4-InBoreWorkspaceChecker-GUI.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
add_subdirectory(InBoreWorkspaceChecker)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
