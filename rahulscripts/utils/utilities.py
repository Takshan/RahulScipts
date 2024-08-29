import os
from glob import glob
from multiprocessing import Pool, cpu_count
from typing import List

import ipywidgets
import numpy as np
import tqdm
from IPython.core.display import HTML
from IPython.display import IFrame, clear_output, display


# check if openbabel is installed
try:
    from openbabel import pybel
except ImportError:
    print("OpenBabel is not installed. Please install it otherwise some functions will not work.")
    command="conda install conda-forge::openbabel"
    print(f"Run this command to install openbabel: {command}")

    # raise ImportError("OpenBabel is not installed. Please install it first.")

from rich import print
from rich.console import Console
from rich.style import Style

console = Console()
base_style = Style.parse("italic magenta bold")


def tarfiles(files, directory=".", verbose=False):
    """tarfiles _summary_

    :param files: _description_
    :type files: _type_
    :param target: _description_
    :type target: _type_
    :return: _description_
    :rtype: _type_
    """
    # import shutil
    import tarfile

    # import tempfile

    base_dir = os.path.dirname(files)
    file_name, file_type = files.rsplit("_", 1)
    file_name = os.path.basename(file_name)
    base_name = os.path.join(base_dir, directory)
    complete_path_filename = os.path.join(base_name, file_name)
    if not os.path.exists(complete_path_filename):
        os.makedirs(complete_path_filename)
    if file_type.startswith("1"):
        suffix = "R1.fastq.gz"
    elif file_type.startswith("2"):
        suffix = "R2.fastq.gz"
    else:
        suffix = "fastq.gz"
    target = f"{complete_path_filename}.{suffix}"
    # good to use temp ut not using for now to save time
    # with tempfile.TemporaryDirectory() as tmpdir:
    with tarfile.open(target, "w:gz") as tar:
        # for file in files:
        # shutil.copy(files, tmpdir)
        tar.add(files)

    if verbose:
        print(f"Save as {target}")
    return target


def tar_for_umi(files: list) -> list:
    """tar_for_umi _summary_"""
    # print(f'starting tar balling on {cpu_count()-1} cores')
    pool = Pool(processes=(int(cpu_count()) - 1))
    return list(
        tqdm.tqdm(pool.imap_unordered(tarfiles, files), total=len(files))
    )


def view_report(
    size: tuple = (800, 1200),
    file_type: str = "html",
    directory: str = "current",
) -> display:
    """view_report _summary_

    :param size: _description_, defaults to (800, 600)
    :type size: tuple, optional
    :param file_type: _description_, defaults to "html"
    :type file_type: str, optional
    :param directory: _description_, defaults to "current"
    :type directory: str, optional
    :return: _description_
    :rtype: display
    """
    directory = os.getcwd() if directory == "current" else directory

    all_files: List = []
    for f in os.listdir(directory):
        if f.endswith(file_type):
            _file = os.path.relpath(
                os.path.join(os.path.join(os.getcwd(), directory), f),
                os.getcwd(),
            )
            all_files.append(_file)

    def on_change(change):
        if change["name"] == "value" and (change["new"] != change["old"]):
            clear_output()
            display(selection)
            console.print(
                f"👉 Showing Report for :{selection.value}",
                style=base_style + Style(underline=True),
            )
            display(IFrame(change["new"], width=size[0], height=size[1]))

    selection = ipywidgets.Dropdown(
        options=all_files,
        description="Select File:",
        disabled=False,
        value=all_files[0],
    )
    display(selection)
    console.print(
        f"👉 Showing Report for :{selection.value}",
        style=base_style + Style(underline=True),
    )
    selection.observe(on_change, names="value")
    display(IFrame(selection.value, width=size[0], height=size[1]))


def centre_of_mass(mol) -> np.ndarray:
    """
    Calculate the centre of mass of a molecule.

    """
    mass = 0
    x = 0
    y = 0
    z = 0
    for atom in mol.atoms:
        if atom is not None:
            mass += atom.atomicmass
            x += atom.coords[0] * atom.atomicmass
            y += atom.coords[1] * atom.atomicmass
            z += atom.coords[2] * atom.atomicmass
    return np.array([x / mass, y / mass, z / mass])


def centroid_of_molecule(mol) -> np.ndarray:
    """
    Calculate the centroid of a molecule.
    """
    x = 0
    y = 0
    z = 0
    for atom in mol.atoms:
        if atom is not None:
            x += atom.coords[0]
            y += atom.coords[1]
            z += atom.coords[2]
    return np.array(
        [x / len(mol.atoms), y / len(mol.atoms), z / len(mol.atoms)]
    )


def file_to_mol(filename, formats=None):
    """file_to_mol _summary_

    :param filename: _description_
    :type filename: _type_
    :param formats: _description_, defaults to None
    :type formats: _type_, optional
    :return: _description_
    :rtype: _type_
    """
    # TODO: check for openbabel molecule name?
    if formats is None:
        formats = filename.split(".")[-1]

    return next(pybel.readfile(format=formats, filename=filename))


def file_search(types=None, target="*", specific=None, BASE_DIR=None):
    """searches files in sub dir
    Args:
        type (str, optional): Search file format
        target (str, optional): Identifier to search
        specific (str, optional): Specific folder to search
    Returns:
        list: Search result
    """
    if BASE_DIR is None:
        BASE_DIR = os.getcwd()
    try:
        if specific is None:
            return sorted(
                glob(f"{BASE_DIR}/**/{target}.{types}", recursive=True)
            )
        else:
            return sorted(
                glob(
                    f"{BASE_DIR}/**/{specific}/{target}.{types}", recursive=True
                )
            )
    except Exception as error:
        print(f"{error} \n File not found anywhere.")


def HideShow_code():
    """HideShow_code _summary_

    :return: _description_
    :rtype: _type_
    """
    toggle_code_str = """
    <form action="javascript:code_toggle()"><input type="submit" id="toggleButton" value="Show|Hide Code"></form>
    """

    toggle_code_prepare_str = """
        <script>
        function code_toggle() {
            if ($('div.cell.code_cell.rendered.selected div.input').css('display')!='none'){
                $('div.cell.code_cell.rendered.selected div.input').hide();
            } else {
                $('div.cell.code_cell.rendered.selected div.input').show();
            }
        }
        </script>

    """
    return display(HTML(toggle_code_prepare_str + toggle_code_str))
