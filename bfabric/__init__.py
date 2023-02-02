from ._version import __version__

name = "bfabricPy"
alias = "suds-py3"

msg = "\033[93m{} version {} (2023-02-02) -- \"{}\"\
    \nCopyright (C) 2014-2023 Functional Genomics Center Zurich\033[0m\n\n"\
    .format(name, __version__, alias)

endpoints = sorted(['access', 'annotation', 'application', 'attachement',
        'barcodes', 'comment', 'container', 'dataset', 'executable',
        'externaljob', 'groupingvar', 'importresource', 'mail',
        'parameter', 'plate', 'project', 'resource', 'sample',
        'workflow', 'workflowstep',
        'storage', 'user', 'workunit', 'charge', 'order', 'instrument'])

# for unit tests
project=403
container=project
application=217

from bfabric.bfabric import Bfabric
from bfabric.bfabric import BfabricWrapperCreator
from bfabric.bfabric import BfabricSubmitter
from bfabric.bfabric import BfabricFeeder

