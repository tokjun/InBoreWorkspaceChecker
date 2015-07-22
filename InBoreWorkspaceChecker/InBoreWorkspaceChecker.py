import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import math
import numpy
from Endoscopy import EndoscopyComputePath

#
# InBoreWorkspaceChecker
#

class InBoreWorkspaceChecker:
  def __init__(self, parent):
    parent.title = "InBoreWorkspaceChecker"
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = ["Junichi Tokuda (BWH)"]
    parent.helpText = """
    This module visualizes the gantry of CT/PET/MRI scanner. 
    """
    parent.acknowledgementText = """
    This work was supported by National Center for Image Guided Therapy (P41EB015898). The module is based on a template developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc. partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent


#
# InBoreWorkspaceCheckerWidget
#

class InBoreWorkspaceCheckerWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.logic = InBoreWorkspaceCheckerLogic()
    self.tag = 0

  def setup(self):
    # Instantiate and connect widgets ...
    
    ####################
    # For debugging
    #
    # Reload and Test area
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)
    
    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "InBoreWorkspaceChecker Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)
    #
    ####################

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Target point (vtkMRMLMarkupsFiducialNode)
    #
    self.DestinationSelector = slicer.qMRMLNodeComboBox()
    self.DestinationSelector.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.DestinationSelector.addEnabled = True
    self.DestinationSelector.removeEnabled = False
    self.DestinationSelector.noneEnabled = True
    self.DestinationSelector.showHidden = False
    self.DestinationSelector.renameEnabled = True
    self.DestinationSelector.selectNodeUponCreation = True
    self.DestinationSelector.showChildNodeTypes = False
    self.DestinationSelector.setMRMLScene( slicer.mrmlScene )
    self.DestinationSelector.setToolTip( "Pick up or create a Model node." )
    parametersFormLayout.addRow("Gantry model: ", self.DestinationSelector)

    #
    # Length of the gantry 
    #
    self.LengthSliderWidget = ctk.ctkSliderWidget()
    self.LengthSliderWidget.singleStep = 1.0
    self.LengthSliderWidget.minimum = 200.0
    self.LengthSliderWidget.maximum = 3000.0
    self.LengthSliderWidget.value = 1200.0
    self.LengthSliderWidget.setToolTip("Length of the gantry")
    parametersFormLayout.addRow("Gantry length (mm): ", self.LengthSliderWidget)

    #
    # Inner Diameter of the gantry
    #
    self.DiameterSliderWidget = ctk.ctkSliderWidget()
    self.DiameterSliderWidget.singleStep = 1.0
    self.DiameterSliderWidget.minimum = 200.0
    self.DiameterSliderWidget.maximum = 100.0
    self.DiameterSliderWidget.value = 700.0
    self.DiameterSliderWidget.setToolTip("Inner diameter of the gantry")
    parametersFormLayout.addRow("Gantry diameter (mm): ", self.DiameterSliderWidget)

    #
    # Offset of the gantry center from the imaging isocenter
    #
    self.CenterOffsetRSliderWidget = ctk.ctkSliderWidget()
    self.CenterOffsetRSliderWidget.singleStep = 1.0
    self.CenterOffsetRSliderWidget.minimum = 0.0
    self.CenterOffsetRSliderWidget.maximum = 100.0
    self.CenterOffsetRSliderWidget.value = 0.0
    self.CenterOffsetRSliderWidget.setToolTip("Offset of the grantry center from the imaging isocenter.")
    parametersFormLayout.addRow("Center offset R (mm): ", self.CenterOffsetRSliderWidget)

    #
    # Offset of the gantry center from the imaging isocenter
    #
    self.CenterOffsetASliderWidget = ctk.ctkSliderWidget()
    self.CenterOffsetASliderWidget.singleStep = 1.0
    self.CenterOffsetASliderWidget.minimum = 0.0
    self.CenterOffsetASliderWidget.maximum = 100.0
    self.CenterOffsetASliderWidget.value = 0.0
    self.CenterOffsetASliderWidget.setToolTip("Offset of the grantry center from the imaging isocenter.")
    parametersFormLayout.addRow("Center offset A (mm): ", self.CenterOffsetASliderWidget)

    #
    # Offset of the gantry center from the imaging isocenter
    #
    self.CenterOffsetSSliderWidget = ctk.ctkSliderWidget()
    self.CenterOffsetSSliderWidget.singleStep = 1.0
    self.CenterOffsetSSliderWidget.minimum = 0.0
    self.CenterOffsetSSliderWidget.maximum = 100.0
    self.CenterOffsetSSliderWidget.value = 0.0
    self.CenterOffsetSSliderWidget.setToolTip("Offset of the grantry center from the imaging isocenter.")
    parametersFormLayout.addRow("Center offset S (mm): ", self.CenterOffsetSSliderWidget)

    #
    # Check box to start visualizing the ablation volume
    #
    self.EnableCheckBox = qt.QCheckBox()
    self.EnableCheckBox.checked = 0
    self.EnableCheckBox.setToolTip("If checked, the InBoreWorkspaceChecker module keeps updating the ablation volume as the points are updated.")
    parametersFormLayout.addRow("Enable", self.EnableCheckBox)

    #
    # Check box to show the slice intersection
    #
    self.SliceIntersectionCheckBox = qt.QCheckBox()
    self.SliceIntersectionCheckBox.checked = 1
    self.SliceIntersectionCheckBox.setToolTip("If checked, intersection of the ablation volume will be displayed on 2D viewers.")
    parametersFormLayout.addRow("Slice Intersection", self.SliceIntersectionCheckBox)

    # Connections
    self.EnableCheckBox.connect('toggled(bool)', self.onEnable)
    self.SliceIntersectionCheckBox.connect('toggled(bool)', self.onEnableSliceIntersection)
    self.DestinationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onDestinationSelected)
    self.LengthSliderWidget.connect("valueChanged(double)", self.onSizeParameterUpdated)
    self.DiameterSliderWidget.connect("valueChanged(double)", self.onSizeParameterUpdated)
    self.CenterOffsetRSliderWidget.connect("valueChanged(double)", self.onSizeParameterUpdated)
    self.CenterOffsetASliderWidget.connect("valueChanged(double)", self.onSizeParameterUpdated)
    self.CenterOffsetSSliderWidget.connect("valueChanged(double)", self.onSizeParameterUpdated)

    # Add vertical spacer
    self.layout.addStretch(1)
    
  def cleanup(self):
    pass

  def onEnable(self, state):
    self.logic.enableAutomaticUpdate(state)

  def onEnableSliceIntersection(self, state):
    self.logic.enableSliceIntersection(state)

  def onDestinationSelected(self):
    # Update destination node
    if self.DestinationSelector.currentNode():
      self.logic.DestinationNode = self.DestinationSelector.currentNode()
      self.logic.DestinationNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onModelModifiedEvent)

    # Update checkbox
    if self.DestinationSelector.currentNode() == None:
      self.EnableCheckBox.setCheckState(False)
    else:
      self.logic.DestinationNode.SetAttribute('InBoreWorkspaceChecker.Length',self.logic.LengthSliderWidget.value)
      self.logic.DestinationNode.SetAttribute('InBoreWorkspaceChecker.Diameter',self.logic.DiameterSliderWidget.value)
      self.logic.DestinationNode.SetAttribute('InBoreWorkspaceChecker.OffsetX',self.logic.DiameterSliderWidget.value)
      self.logic.updateAblationVolume()

  def onSizeParameterUpdated(self):
    self.logic.setSize(self.LengthSliderWidget.value, self.DiameterSliderWidget.value)
    self.logic.setCenterOffset(self.CenterOffsetSliderWidget.value)

  def onReload(self,moduleName="InBoreWorkspaceChecker"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onModelModifiedEvent(self, caller, event):
    pass



#
# InBoreWorkspaceCheckerLogic
#

class InBoreWorkspaceCheckerLogic:

  def __init__(self):
    self.SourceNode = None
    self.DestinationNode = None
    self.TubeRadius = 5.0

    self.MajorAxis = 30.0
    self.MinorAxis = 20.0
    self.TipOffset = 0.0

    self.AutomaticUpdate = False
    self.NumberOfIntermediatePoints = 20
    self.ModelColor = [0.0, 0.0, 1.0]

    self.SphereSource = None
    self.SliceIntersection = True
    
  def setNumberOfIntermediatePoints(self,npts):
    if npts > 0:
      self.NumberOfIntermediatePoints = npts
    self.updateAblationVolume()

  def setSize(self, majorAxis, minorAxis):
    self.MajorAxis = majorAxis
    self.MinorAxis = minorAxis
    self.updateAblationVolume()
    
  def setTipOffset(self, offset):
    self.TipOffset = offset
    self.updateAblationVolume()

  def enableAutomaticUpdate(self, auto):
    self.AutomaticUpdate = auto
    self.updateAblationVolume()

  def enableSliceIntersection(self, state):
    if self.DestinationNode.GetDisplayNodeID() == None:
      modelDisplayNode = slicer.vtkMRMLModelDisplayNode()
      modelDisplayNode.SetColor(self.ModelColor)
      slicer.mrmlScene.AddNode(modelDisplayNode)
      self.DestinationNode.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())
    
    displayNodeID = self.DestinationNode.GetDisplayNodeID()
    displayNode = slicer.mrmlScene.GetNodeByID(displayNodeID)
    if displayNode != None:
      if state:
        displayNode.SliceIntersectionVisibilityOn()
      else:
        displayNode.SliceIntersectionVisibilityOff()
    

  def controlPointsUpdated(self,caller,event):
    if caller.IsA('vtkMRMLAnnotationRulerNode') and event == 'ModifiedEvent':
      self.updateAblationVolume()

  def computeTransform(self, pTip, pTail, offset, transform):
    v1 = [0.0, 0.0, 0.0]
    vtk.vtkMath.Subtract(pTip, pTail, v1)
    vtk.vtkMath.Normalize(v1)
    v2 = [0.0, 0.0, 1.0]
    axis = [0.0, 0.0, 0.0]

    #vtk.vtkMath.Cross(v1, v2, axis)
    vtk.vtkMath.Cross(v2, v1, axis)
    #angle = vtk.vtkMath.AngleBetweenVectors(v1, v2) # This does not work
    s = vtk.vtkMath.Norm(axis)
    c = vtk.vtkMath.Dot(v1, v2)
    angle = math.atan2(s, c)

    tipOffset = v1
    vtk.vtkMath.MultiplyScalar(tipOffset, offset)
    transform.PostMultiply()
    transform.RotateWXYZ(angle*180.0/math.pi, axis)
    transform.Translate(pTip)
    transform.Translate(tipOffset)

  def updateAblationVolume(self):

    if self.AutomaticUpdate == False:
      return

    if self.SourceNode and self.DestinationNode:

      pTip = [0.0, 0.0, 0.0]
      pTail = [0.0, 0.0, 0.0]
      #self.SourceNode.GetNthFiducialPosition(0,pTip)
      self.SourceNode.GetPosition1(pTip)
      #self.SourceNode.GetNthFiducialPosition(1,pTail)
      self.SourceNode.GetPosition2(pTail)
      
      if self.DestinationNode.GetDisplayNodeID() == None:
        modelDisplayNode = slicer.vtkMRMLModelDisplayNode()
        modelDisplayNode.SetColor(self.ModelColor)
        slicer.mrmlScene.AddNode(modelDisplayNode)
        self.DestinationNode.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())
        
      displayNodeID = self.DestinationNode.GetDisplayNodeID()
      modelDisplayNode = slicer.mrmlScene.GetNodeByID(displayNodeID)

      if modelDisplayNode != None and self.SliceIntersection == True:
        modelDisplayNode.SliceIntersectionVisibilityOn()
      else:
        modelDisplayNode.SliceIntersectionVisibilityOff()
        
      if self.SphereSource == None:  
        self.SphereSource = vtk.vtkSphereSource()
        self.SphereSource.SetThetaResolution(20)
        self.SphereSource.SetPhiResolution(20)
        self.SphereSource.Update()
        
      # Scale sphere to make ellipsoid
      scale = vtk.vtkTransform()
      scale.Scale(self.MinorAxis, self.MinorAxis, self.MajorAxis)
      scaleFilter = vtk.vtkTransformPolyDataFilter()
      scaleFilter.SetInputConnection(self.SphereSource.GetOutputPort())
      scaleFilter.SetTransform(scale)
      scaleFilter.Update();
      
      # Transform
      transform = vtk.vtkTransform()
      self.computeTransform(pTip, pTail, self.TipOffset, transform)
      transformFilter = vtk.vtkTransformPolyDataFilter()
      transformFilter.SetInputConnection(scaleFilter.GetOutputPort())
      transformFilter.SetTransform(transform)
      transformFilter.Update();
      
      self.DestinationNode.SetAndObservePolyData(transformFilter.GetOutput())
      self.DestinationNode.Modified()
      
      if self.DestinationNode.GetScene() == None:
        slicer.mrmlScene.AddNode(self.DestinationNode)

        
