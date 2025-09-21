class ApiReference:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @property
    def users(self):
        return self.url("users")

    def user(self, user_id: int):
        return self.url(f"users/{user_id}")

    @property
    def posts(self):
        return self.url("posts")

    def post(self, post_id: int):
        return self.url(f"posts/{post_id}")

    @property
    def discussions(self):
        return self.url("discussions")

    @property
    def discussions_last(self):
        return self.url("discussions?include=user,lastPostedUser,tags,tags.parent,recipientUsers,recipientGroups,firstPost&sort=-createdAt&page[offset]=0")

    def discussion(self, discussion_id: int):
        return self.url(f"discussions/{discussion_id}")
