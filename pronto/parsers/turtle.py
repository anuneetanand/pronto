from rdflib import Graph
from .base import BaseParser
from pronto.parsers.rdfxml import RdfXMLParser
class TurtleParser(BaseParser):
    @classmethod
    def can_parse(cls, path, buffer):
        return path.endswith('.ttl')

    def parse_from(self, handle, threads=None):
        ttl_data = Graph()
        ttl_data.parse(handle, format='ttl')
        rdfxml_data = ttl_data.serialize(format='xml')
        rdfxml_parser = RdfXMLParser()
        print(rdfxml_parser.__dict__)
        rdfxml_parser.parse_from(rdfxml_data, threads=threads)
