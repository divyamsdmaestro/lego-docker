from apps.common.models.base import SoftDeleteModel, UniqueNameModel

class City(UniqueNameModel, SoftDeleteModel):
    """A city model contains unique names and soft deletions"""
    pass