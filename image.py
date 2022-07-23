class Image:
    filename: str
    url: str

    def __init__(self, filename: str, url: str) -> None:
        self.filename = filename
        self.url = url
