"""
Communicate between Python and Javascript asynchronously using
inter-process messaging with the use of Javascript Bindings.
"""

from cefpython3 import cefpython as cef
import platform
import sys
import os
from electrolens.converter import Converter


def check_versions():
    ver = cef.GetVersion()
    print("[ElectroLens] CEF Python {ver}".format(ver=ver["version"]))
    print("[ElectroLens] Chromium {ver}".format(ver=ver["chrome_version"]))
    print("[ElectroLens] CEF {ver}".format(ver=ver["cef_version"]))
    print("[ElectroLens] Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"

def view(data, show_dev_tools = False, save_config = True, config_filename = "config.json"):
    print("[ElectroLens] Starting...")
    check_versions()

    converter = Converter(data)
    config = converter.convert()

    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    settings = {
        #"debug": True,
        #"log_severity": cef.LOGSEVERITY_INFO,
        #"log_file": "debug.log",
        #"remote_debugging_port":8080,
    }
    cef.Initialize(settings=settings)
    cwd = os.getcwd()

    browser_setting = { "file_access_from_file_urls_allowed":True,\
                    "universal_access_from_file_urls_allowed": True,\
                    "web_security_disabled":True}
    dir_path = os.path.dirname(__file__).replace("\\","/")
    index_filepath = "file://" + os.path.join(dir_path, 'static/index_cefpython_clean.html')
    print(index_filepath)
    browser = cef.CreateBrowserSync(url=index_filepath,
                                    window_title="ElectroLens",
                                    settings = browser_setting)
    browser.SetClientHandler(LoadHandler(config))
    if show_dev_tools:
        browser.ShowDevTools()
    cef.MessageLoop()
    # del browser
    cef.Shutdown()
    return

def trajToConfig2(data):
    a, fingerprint = data
    #print "converting traj to config"
    systemDimension = {}
    systemDimension["x"] = [0,a.cell[0][0]]
    systemDimension["y"] = [0,a.cell[1][1]]
    systemDimension["z"] = [0,a.cell[2][2]]


    config = {}

    config["views"] = []
    temp = {}
    temp["viewType"] = "3DView"
    temp["moleculeName"] = "test"
    temp["moleculeData"] = {}
    temp["moleculeData"]["data"] = []
    atoms = a
    for i, atom in enumerate(atoms):
        temp_atom = {}
        temp_atom["x"] = atom.position[0]
        temp_atom["y"] = atom.position[1]
        temp_atom["z"] = atom.position[2]
        temp_atom["atom"] = atom.symbol
        temp_atom["p1"] = fingerprint[i][1][0]
        temp_atom["p2"] = fingerprint[i][1][1]
        temp_atom["p3"] = fingerprint[i][1][2]
        temp["moleculeData"]["data"].append(temp_atom)
    temp["moleculeData"]["gridSpacing"] = {"x":0.1,"y":0.1,"z":0.1}
    temp["systemDimension"] = systemDimension
    config["views"].append(temp)
    config["plotSetup"] = {}
    config["plotSetup"]["moleculePropertyList"] = ["atom","p1","p2","p3"]



    return config

class LoadHandler(object):

    def __init__(self, config):
        self.config = config
    #def OnLoadEnd(self, browser, **_):
    #    browser.ExecuteFunction("defineData", self.config)
    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        if not is_loading:
            # Loading is complete. DOM is ready.
            browser.ExecuteFunction("defineData", self.config)
