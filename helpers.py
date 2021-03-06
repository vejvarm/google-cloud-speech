import logging
import re
import time
from typing import Sequence


def console_logger(name=__name__, level=logging.WARNING):

    if not isinstance(level, (str, int)):
        raise TypeError("Logging level data type is not recognised. Should be str or int.")

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level)
    formatter = logging.Formatter('%(levelname)7s (%(name)s) %(asctime)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


def kw_spotter(sentences: Sequence[str], kws: Sequence[str]):
    """ Extract given keywords from sentences

    :param sentences: (List[str]) sentences from which the keywords are extracted
    :param kws: (List[str]) List of keywords compatible with regexp notation
    :return: (List[str]) List of string of keywords extracted from sentences
    """

    matched_keywords = []
    for sent in sentences:
        matches = []
        for kw in kws:
            matches.extend(re.findall(kw, sent, flags=re.I))

        matched_keywords.append(" ".join(matches))

    return matched_keywords


def kw_decoder(matched_kws, dvc_map, loc_map, cmd_map):
    """

    :param matched_kws: (List[List[str]]) match keywords from one or more sentences
    :param dvc_map: (Dict[rstr: str]) map of devices to their names
    :param loc_map (Dict[rstr: str]) map of location commands to their names
    :param cmd_map: (Dict[rstr: str]) map of device commands to their values
    :return: (List[List[str]]) decoded commands
    """
    dc_results = []
    for sent in matched_kws:
        device = None
        locations = []
        command = []
        for dvc_key, dvc_name in dvc_map.items():
            match = re.search(dvc_key, sent, re.I)
            if match:
                device = dvc_name
                sent = re.sub(dvc_key, "", sent, flags=re.I)
                break
        if device:
            current_device = cmd_map[device]

            for loc_key, loc_name in loc_map.items():
                match = re.search(loc_key, sent, re.I)
                if match:
                    locations.append(loc_name)
                    sent = re.sub(loc_key, "", sent, flags=re.I)

            for cmd_key, cmd_val in current_device.items():
                for cmd in re.finditer(cmd_key, sent, flags=re.I):
                    if "_val" in cmd_val:
                        command.append(cmd[0])
                    else:
                        command.append(cmd_val)

        else:
            print("Zařízení nenalezeno. Ignoruji příkaz.")
            continue
        dc_results.append((device, locations, " ".join(command)))
    return dc_results


if __name__ == '__main__':
    device_map = {r"\bkonvic": "kettle",
                  r"\bsvětl": "light"}
    location_map = {r"\bložnic": "bedroom",
                    r"\bobýv": "livingroom",
                    r"\bkuchyň": "kitchen",
                    r"\b(všechn|všud)": "everyroom"}
    command_map = {"kettle": {r"\bpřevař": "boil"},
                   "light": {r"\b(zapn|rozsv)": "on", r"\b(vypn|zavř|zhasn)": "off"}}

    sentences = ["konvici převař na 80 stupňů", "rozsviť světla", "světla zhasni v obýváku", "zavři světla"]
    keywords = [r'\d{1,3}']
    for device in device_map.keys():
        keywords.append(device)
    for location in location_map.keys():
        keywords.append(location)
    for commands in command_map.values():
        for k in commands.keys():
            keywords.append(k)

    matched_kws = kw_spotter(sentences, keywords)

    dc_results = kw_decoder(matched_kws, device_map, location_map, command_map)

    print(dc_results)