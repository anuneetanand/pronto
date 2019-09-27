
import datetime
from typing import Dict, List, Optional, Set

import fastobo

from .synonym import SynonymType
from .pv import PropertyValue
from .utils.impl import set


class Subset(object):

    name: str
    description: str

    __slots__ = ("__weakref__",) + tuple(__annotations__)  # noqa: E0602

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description

    def __eq__(self, other):
        if isinstance(other, Subset):
            return (self.name, self.description) == (other.name, other.description)
        return False

    def __lt__(self, other):
        if not isinstance(other, Subset):
            return NotImplemented
        return (self.name, self.description) < (other.name, other.description)

    def __hash__(self):
        return hash((self.name, self.description))


class Metadata(object):
    format_version: str
    data_version: Optional[str]
    ontology: Optional[str]
    date: Optional[datetime.datetime]
    default_namespace: Optional[str]
    namespace_id_rule: Optional[str]
    owl_axioms: List[str]
    saved_by: Optional[str]
    auto_generated_by: Optional[str]
    subsetdefs: Set[Subset]
    imports: Set[str]
    synonymtypedefs: Set[SynonymType]
    idspaces: Dict[str, str]
    remarks: Set[str]
    annotations: Set[PropertyValue]
    unreserved: Dict[str, Set[str]]

    @classmethod
    def _from_ast(cls, header: fastobo.header.HeaderFrame) -> 'Metadata':
        metadata = cls()

        def copy(src, dst=None, cb=None):
            cb = cb or (lambda x: x)
            dst = dst or src
            return lambda c: setattr(metadata, dst, cb(getattr(c, src)))

        def add(src, dst=None, cb=None):
            cb = cb or (lambda x: x)
            dst = dst or src
            return lambda c: getattr(metadata, dst).add(cb(getattr(c, src)))

        def todo():
            return lambda c: print("todo", c)

        _callbacks = {
            fastobo.header.AutoGeneratedByClause:
                copy("name", "auto_generated_by"),
            fastobo.header.DataVersionClause:
                copy("version", "data_version"),
            fastobo.header.DateClause: copy("date"),
            fastobo.header.DefaultNamespaceClause:
                copy("namespace", "default_namespace", cb=str),
            fastobo.header.FormatVersionClause:
                copy("version", "format_version"),
            fastobo.header.IdspaceClause: (lambda c: (
                metadata.idspace.__setitem__(str(c.prefix), str(c.url))
            )),
            fastobo.header.ImportClause: add("reference", "imports"),
            fastobo.header.OntologyClause: copy("ontology"),
            fastobo.header.OwlAxiomsClause:
                lambda c: metadata.owl_axioms.append(c.axioms),
            fastobo.header.PropertyValueClause: (lambda c: (
                metadata.annotations.add(
                    PropertyValue._from_ast(c.property_value)
                )
            )),
            fastobo.header.RemarkClause: add("remark", "remarks"),
            fastobo.header.SavedByClause: copy("name", "saved_by"),
            fastobo.header.SubsetdefClause: (lambda c: (
                metadata.subsetdefs.add(Subset(str(c.subset), c.description))
            )),
            fastobo.header.SynonymTypedefClause: (lambda c: (
                metadata.synonymtypedefs.add(
                    SynonymType(str(c.typedef), c.description, c.scope)
                )
            )),
            fastobo.header.TreatXrefsAsEquivalentClause: todo(),
            fastobo.header.TreatXrefsAsGenusDifferentiaClause: todo(),
            fastobo.header.TreatXrefsAsHasSubclassClause: todo(),
            fastobo.header.TreatXrefsAsIsAClause: todo(),
            fastobo.header.TreatXrefsAsRelationshipClause: todo(),
            fastobo.header.TreatXrefsAsReverseGenusDifferentiaClause: todo(),
            fastobo.header.NamespaceIdRuleClause:
                copy("rule", "namespace_id_rule"),
            fastobo.header.UnreservedClause: (lambda c: (
                metadata.unreserved
                    .setdefault(c.raw_tag(), set())
                    .add(c.raw_value())
            )),
        }

        for clause in header:
            try:
                _callbacks[type(clause)](clause)
            except KeyError:
                raise TypeError(f"unexpected type: {type(clause).__name__}")

        return metadata

    def __init__(
        self,
        format_version: str = "1.4",
        data_version: Optional[str] = None,
        ontology: Optional[str] = None,
        date: Optional[datetime.datetime] = None,
        default_namespace: Optional[str] = None,
        namespace_id_rule: Optional[str] = None,
        owl_axioms: Optional[List[str]] = None,
        saved_by: Optional[str] = None,
        auto_generated_by: Optional[str] = None,
        subsetdefs: Set[Subset] = None,
        imports: Optional[Dict[str, str]] = None,
        synonymtypedefs: Set[SynonymType] = None,
        idspace: Dict[str, str] = None,
        remarks: Set[str] = None,
        annotations: Set[PropertyValue] = None,
        **unreserved: Set[str],
    ):
        self.format_version = format_version
        self.data_version = data_version
        self.ontology = ontology
        self.date = date
        self.default_namespace = default_namespace
        self.namespace_id_rule = namespace_id_rule
        self.owl_axioms = owl_axioms or list()
        self.saved_by = saved_by
        self.auto_generated_by = auto_generated_by
        self.subsetdefs = set(subsetdefs) if subsetdefs is not None else set()
        self.imports = set(imports) if imports is not None else set()
        self.synonymtypedefs = set(synonymtypedefs) if synonymtypedefs is not None else set()
        self.idspace = idspace or dict()
        self.remarks = remarks or set()
        self.annotations = annotations or set()
        self.unreserved = unreserved
