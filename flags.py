class FLAGS:
    # switch between online and offline mode
    offline = False

    # manual audio settings
    streaming_limit = 240000  # 4 minutes
    sample_rate = 16000  # Hz
    chunk_size = int(sample_rate / 10)  # 100ms

    # authentication settings
    # google_cloud_auth_key = "./keys/speech2text-1597656821253-be85a49eb749.json"  # notebook
    google_cloud_auth_key = "./keys/speech2text-1597656821253-4168b13db8f6.json"  # desktop


    # keyword spotting settings
    device_map = {r"\bkonvic": "kettle",
                  r"\b(světl|světe)": "light"}
    location_map = {r"\bložnic": "bedroom",
                    r"\bobýv": "livingroom",
                    r"\bkuchy[nň]": "kitchen",
                    r"\b(všech|všud)": "everyroom"}
    command_map = {"kettle": {r"\bpřevař": "boil", r'\b\d{1,3}\b': "_val"},
                   "light": {r"\b(zapn|rozsv)": "turnon",
                             r"\b(vypn|zavř|zhasn)": "turnoff",
                             r"\b(barv|rgb)": "rgb",
                             r"\bteplot": "colortemp",
                             r"\b(jas|intenzit|svítiv)": "brightness",
                             r'\b\d{1,3}\b': "_val",
                             r'\b\d{4}\b': "_val"}}

    # automatic inference
    keywords = []
    for device in device_map.keys():
        keywords.append(device)
    for location in location_map.keys():
        keywords.append(location)
    for commands in command_map.values():
        for k in commands.keys():
            keywords.append(k)
    keywords = set(keywords)

    # wiz light ip adresses
    lights = {"kitchen": "192.168.1.202",
              "bedroom": "192.168.1.243",
              "livingroom": "192.168.1.249"}
