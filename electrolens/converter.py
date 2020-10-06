import json
import os
import csv
from ase import Atoms
from ase.io.trajectory import TrajectoryReader
from sklearn.preprocessing import normalize


def atom_config(atom):
    return {"x": atom.position[0], "y": atom.position[1], "z": atom.position[2], "atom": atom.symbol}


class Converter(object):
    def __init__(self, data):
        self.data = data
        if isinstance(data, Atoms):
            self.framed = False
        elif isinstance(data, TrajectoryReader):
            self.framed = True

    def convert(self):
        if self.framed:
            print("[Converter] Converting framed data to config")
            return self.to_config(lattice_constants=self.data[0].cell.lengths(),
                                  lattice_vector=normalize(self.data[0].cell, axis=1))
        else:
            print("[Converter] Converting non-framed data to config")
            return self.to_config(lattice_constants=self.data.cell.lengths(),
                                  lattice_vector=normalize(self.data.cell, axis=1))

    def to_config(self, lattice_constants, lattice_vector):
        system_dimension = {"x": lattice_constants[0], "y": lattice_constants[1], "z": lattice_constants[2]}

        # configuration dictionary to be returned
        config = {"views": [], "plotSetup": {"moleculePropertyList": ["atom"]}}

        # temporary dictionary to hold nested JSON - will eventually go in config["views"]
        temp = {"viewType": "3DView", "moleculeName": "test", "moleculeData": {}, "systemLatticeVectors": {},
                "systemDimension": system_dimension}

        # initialize list of molecular data to store
        temp["moleculeData"]["data"] = []

        # todo: necessary? do not see it show up in created JSON file
        temp["systemLatticeVectors"]["u11"] = lattice_vector[0][0]
        temp["systemLatticeVectors"]["u12"] = lattice_vector[0][1]
        temp["systemLatticeVectors"]["u13"] = lattice_vector[0][2]
        temp["systemLatticeVectors"]["u21"] = lattice_vector[1][0]
        temp["systemLatticeVectors"]["u22"] = lattice_vector[1][1]
        temp["systemLatticeVectors"]["u23"] = lattice_vector[1][2]
        temp["systemLatticeVectors"]["u31"] = lattice_vector[2][0]
        temp["systemLatticeVectors"]["u32"] = lattice_vector[2][1]
        temp["systemLatticeVectors"]["u33"] = lattice_vector[2][2]

        # collect all atoms in the input data
        atom_count = 0
        if self.framed:
            # data is essentially a 2D array - each row represents a set of atoms at a particular frame
            num_frames = len(self.data)
            length = num_frames * len(self.data[0])
            print(f"[Converter] Received framed input data with {length} items over {num_frames} frames")

            # todo: what is the significance of this number?
            if length < 10000000:
                for frame in range(num_frames):
                    for atom in self.data[frame]:
                        atom_count += 1
                        temp_atom = atom_config(atom)
                        # add the frame number to the JSON for this atom
                        temp_atom["frame"] = frame
                        temp["moleculeData"]["data"].append(temp_atom)
            else:
                temp["moleculeData"]["dataFilename"] = os.getcwd() + "/__ElectroLens_View_Intermediate__.csv"
                with open("__ElectroLens_View_Intermediate__.csv", mode="w") as file:
                    writer = csv.writer(file, delimiter=",")
                    writer.writerow(["x", "y", "z", "atoms", "frame"])

                    for frame in range(num_frames):
                        for atom in self.data[frame]:
                            atom_count += 1
                            temp_row = [atom.position[0], atom.position[1], atom.position[2], atom.symbol, frame]
                            writer.writerow(temp_row)

            # add some extra configuration specific to framed data
            config["plotSetup"]["frameProperty"] = "frame"
            config["plotSetup"]["moleculePropertyList"].append("frame")
        else:
            # data presented as just a list
            print(f"[Converter] Received input data with {len(self.data)} items")
            for atom in self.data:
                atom_count += 1
                # add the data to config file
                temp["moleculeData"]["data"].append(atom_config(atom))
        print(f"[Converter] Successfully processed {atom_count} items")

        # add all of the molecular data found to the config file
        config["views"].append(temp)

        # dump the data into a re-usable JSON file
        with open("temp_data.json", "w") as fp:
            print("[Converter] Writing config to temp_data.json")
            json.dump(config, fp, indent=4)

        return config

