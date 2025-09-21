class RequestFormatter:
    @staticmethod
    def format_status(status: int) -> str:
        return {
            200: "Success",
            201: "Created",
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            405: "Method not allowed",
            500: "Internal server error",
        }.get(status, f"Unknown error (code {status})")