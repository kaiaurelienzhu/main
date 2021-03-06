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
Set the parameters for an Additional Dehumidification Element. Sets the values on the 'Cooling Unit' worksheet.
-
EM August 11, 2020
    Args:
        wasteHeatToRoom_: ('x' or '') Default=''. If this field is checked, then the waste heat from the dehumidification unit will be considered as an internal heat gain. On the contrary, dehumidification has no influence on the thermal balance.
        SEER_: Default=1. 1 litre water per kWh electricity result in an energy efficiency ratio of 0.7. Good devices, e.g. with internal heat recovery, achieve values of up to 2.
    Returns:
        dehumidCooling_: 
"""

ghenv.Component.Name = "BT_CreateCooling_Dehumidification"
ghenv.Component.NickName = "Cooling | Dehumid"
ghenv.Component.Message = 'AUG_11_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import scriptcontext as sc
import Grasshopper.Kernel as ghK

# Classes and Defs
preview = sc.sticky['Preview']

class Cooling_Dehumidification:
    def __init__(self, _waste='', _seer=3):
        self.WasteHeatToRoom = _waste
        self.SEER = _seer
    
    def getValsForPHPP(self):
        return self.WasteHeatToRoom, self.SEER
    
    def __repr__(self):
        return "A Cooling: Dehumidification Params Object"

def cleanInputs(_in, _nm, _default):
    # Apply defaults if the inputs are Nones
    out = _in if _in != None else _default
    
    if _nm == 'waste':
        if out in ['x', '']:
            return out
        else:
            msg = "on_offModel_ input should be either 'x' or '' (blank) only.\n"\
            "If this field is checked, then the waste heat from the dehumidification\n"\
            "unit will be considered as an internal heat gain. On the contrary,\n"
            "dehumidification has no influence on the thermal balance."
            
            ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, msg)
            return _default
    
    try:
        return float(out)
    except:
        ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, '"{}" input should be a number'.format(_nm))
        return _default

waste = cleanInputs(wasteHeatToRoom_, 'waste', '')
seer = cleanInputs(SEER_, 'SEER_', 3)

dehumidCooling_ = Cooling_Dehumidification(waste, seer)

preview(dehumidCooling_)
