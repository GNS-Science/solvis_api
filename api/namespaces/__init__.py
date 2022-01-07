from flask_restx import Api

from .locations import locations, location_lists
from .radii import api as radii
from .solutions import api as solutions

api = Api(
    title='Solvis API',
    version='0.1',
    description='A solvis Rest API',
    # All API metadatas
)

api.add_namespace(locations)
api.add_namespace(location_lists)
api.add_namespace(radii)
api.add_namespace(solutions)
