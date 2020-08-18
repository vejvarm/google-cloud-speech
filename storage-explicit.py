AUTH_PATH = "C:/!Cloud/keys/Speech2Text-bb59621b56c2.json"


def explicit():
    from google.cloud import storage

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        AUTH_PATH)

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)


if __name__ == '__main__':
    explicit()