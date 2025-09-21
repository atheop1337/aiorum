from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.reply_post_id = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attr_dict = dict(attrs)
            if attr_dict.get("class") == "PostMention" and "data-id" in attr_dict:
                self.reply_post_id = attr_dict["data-id"]

    def handle_data(self, d):
        self.result.append(d)

    def get_data(self):
        return ''.join(self.result).strip()

    def get_reply_id(self):
        return self.reply_post_id

    @staticmethod
    def strip_html_and_extract_reply_id(html: str) -> tuple[str, str | None]:
        stripper = HTMLStripper()
        stripper.feed(html)
        return stripper.get_data(), stripper.get_reply_id()