#
# IDF2PHPP: A Plugin for exporting an EnergyPlus IDF file to the Passive House Planning Package (PHPP). Created by blgdtyp, llc
# 
# This component is part of IDF2PHPP.
# 
# Copyright (c) 2020, bldgtyp, llc <info@bldgtyp.com> 
# IDF2PHPP is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# IDF2PHPP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# For a copy of the GNU General Public License
# see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
Creates DHW Branch Piping sets for the 'DHW+Distribution' PHPP worksheet. Can create up to 5 branch piping sets. Will take in a DataTree of curves from Rhino and calculate their lengths automatically. Will try and pull curve object attributes from Rhino as well - use attribute setter to assign the pipe diameter, insulation, etc... on the Rhino side.
-
EM August 10, 2020
    Args:
        pipe_geom_: <Tree> (Curves) A DataTree with each branch containing curves for one 'set' of recirculation piping. PHPP allows up to 5 'sets' of recirc piping. Each 'set' should include the forward and return piping curves for that distribution leg (ideally as a single continuous curve/loop)
        Use the 'Entwine' component to organize geometry into branches before inputing if more than one set of piping. Use an 'ID' component before inputting Rhino geometry.
        diameter_: (m) The nominal size of the branch piping. Default is 0.0127m (1/2").
        tapOpenings_: The number of tap openings / person every day. Default is 6 openings/person/day.
        utilisation_: The days/year the DHW system is operational. Defauly is 365 days/year.
    Returns:
        branch_piping_: The Branch Piping object(s). Connect this to the 'branch_piping_' input on the 'DHW System' component in order to pass along to the PHPP.
"""

ghenv.Component.Name = "BT_DHW_Piping_Banches"
ghenv.Component.NickName = "Piping | Branches"
ghenv.Component.Message = 'AUG_10_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import Rhino
import scriptcontext as sc
from contextlib import contextmanager
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper.Kernel as ghK

# Classes and Defs
preview = sc.sticky['Preview']
PHPP_DHW_branch_piping = sc.sticky['PHPP_DHW_branch_piping']

@contextmanager
def rhDoc():
    try:
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        yield
    finally:
        sc.doc = ghdoc

def cleanInputs(_in, _nm, _default):
    # Apply defaults if the inputs are Nones
    out = _in if _in != None else _default
    
    # Check that output can be float
    try:
        out = float(out)
        # Check units
        if _nm == "diameter_":
            if out > 1:
                unitWarning = "Check diameter units? Should be in METERS not MM." 
                ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, unitWarning)
        return out
    except:
        ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, '"{}" input should be a number'.format(_nm))
        return out

def getTotalPipeLength(_branch):
    temp = []
    for geom_input in _branch:
        try:
            temp.append( float(geom_input) )
        except:
            if isinstance(geom_input, Rhino.Geometry.Curve):
                crv = rs.coercecurve(geom_input)
                pipeLen = ghc.Length(crv)
            else:
                pipeLen = False
            
            if not pipeLen:
                crvWarning = "Something went wrong getting the Pipe Geometry length?\n"\
                "Please ensure you are passing in only curves / polyline objects or numeric values.?"
                ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, crvWarning)
            else:
                temp.append(pipeLen)
        
    return temp

def main(_pipe_geom, _openings, _util, _diam):
    branch_piping = []
    with rhDoc():
        for branch in _pipe_geom.Branches:
            totalLength = getTotalPipeLength(branch)
            
            # Create the Branch Piping Object
            obj = PHPP_DHW_branch_piping()
            obj.totalLength = sum(totalLength)
            obj.totalTapPoints = len(branch)
            obj.tapOpenings = _openings
            obj.utilisation = _util
            obj.diameter = _diam
            
            branch_piping.append(obj)
    return branch_piping

# Input Defaults, Warnings
diam = cleanInputs(diameter_, "diameter_", 0.0127)
openings = cleanInputs(tapOpenings_, "tapOpenings_", 6)
util = cleanInputs(utilisation_, "utilisation_", 365)

# Main
if pipe_geom_.BranchCount > 0:
    branch_piping_ = main(pipe_geom_, openings, util, diam)

if branch_piping_:
    for obj in branch_piping_:
        print('----\nDHW Branch Piping:')
        preview(obj)
