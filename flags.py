class FLAGS:
    # manual audio settings
    streaming_limit = 240000  # 4 minutes
    sample_rate = 16000  # Hz
    chunk_size = int(sample_rate / 10)  # 100ms

    # authentication settings
    google_cloud_auth_key = "./keys/speech2text-1597656821253-be85a49eb749.json"

    # keyword spotting settings
    device_map = {r"\bkonvic": "kettle",
                  r"\bsvětl": "light"}
    command_map = {"kettle": {r"\bpřevař": "boil", r'\b\d{1,3}\b': "_val"},
                   "light": {r"\b(zapn|rozsv)": "on", r"\b(vypn|zavř|zhasn)": "off"}}

    # automatic inference
    keywords = []
    for k in device_map.keys():
        keywords.append(k)
    for commands in command_map.values():
        for k in commands.keys():
            keywords.append(k)
