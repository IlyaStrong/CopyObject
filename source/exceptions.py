class AbortedException(Exception):
    def __init__(self, message="Операция отменена"):
        super().__init__(message)
