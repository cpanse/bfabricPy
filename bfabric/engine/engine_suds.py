from __future__ import annotations

import copy
from typing import Any

from suds import MethodNotFound
from suds.client import Client
from suds.serviceproxy import ServiceProxy

from bfabric.bfabric_config import BfabricAuth
from bfabric.engine.response_format_suds import suds_asdict_recursive
from bfabric.errors import BfabricRequestError, get_response_errors
from bfabric.results.result_container import _clean_result, ResultContainer


class EngineSUDS:
    """B-Fabric API SUDS Engine."""

    def __init__(self, base_url: str, drop_underscores: bool = True) -> None:
        self._cl = {}
        self._base_url = base_url
        self._drop_underscores = drop_underscores

    def read(
        self,
        endpoint: str,
        obj: dict[str, Any],
        auth: BfabricAuth,
        page: int = 1,
        idonly: bool = False,
        includedeletableupdateable: bool = False,
    ) -> ResultContainer:
        """Reads the requested `obj` from `endpoint`.
        :param endpoint: the endpoint to read, e.g. `workunit`, `project`, `order`, `externaljob`, etc.
        :param obj: a python dictionary which contains all the attribute values that have to match
        :param auth: the authentication handle of the user performing the request
        :param page: the page number to read
        :param idonly: whether to return only the ids of the objects
        :param includedeletableupdateable: TODO
        """
        query = copy.deepcopy(obj)
        query["includedeletableupdateable"] = includedeletableupdateable

        full_query = dict(login=auth.login, page=page, password=auth.password, query=query, idonly=idonly)
        service = self._get_suds_service(endpoint)
        response = service.read(full_query)
        return self._convert_results(response=response, endpoint=endpoint)

    # TODO: How is client.service.readid different from client.service.read. Do we need this method?
    def readid(self, endpoint: str, query: dict, auth: BfabricAuth, page: int = 1) -> ResultContainer:
        query = dict(login=auth.login, page=page, password=auth.password, query=query)
        service = self._get_suds_service(endpoint)
        response = service.readid(query)
        return self._convert_results(response=response, endpoint=endpoint)

    def save(self, endpoint: str, obj: dict, auth: BfabricAuth) -> ResultContainer:
        query = {"login": auth.login, "password": auth.password, endpoint: obj}
        service = self._get_suds_service(endpoint)
        try:
            response = service.save(query)
        except MethodNotFound as e:
            raise BfabricRequestError(f"SUDS failed to find save method for the {endpoint} endpoint.") from e
        return self._convert_results(response=response, endpoint=endpoint)

    def delete(self, endpoint: str, id: int | list[int], auth: BfabricAuth) -> ResultContainer:
        if isinstance(id, list) and len(id) == 0:
            print("Warning, attempted to delete an empty list, ignoring")
            # TODO maybe use error here (and make sure it's consistent)
            return ResultContainer([], total_pages_api=0)

        query = {"login": auth.login, "password": auth.password, "id": id}
        service = self._get_suds_service(endpoint)
        response = service.delete(query)
        return self._convert_results(response=response, endpoint=endpoint)

    def _get_suds_service(self, endpoint: str) -> ServiceProxy:
        """Returns a SUDS service for the given endpoint. Reuses existing instances when possible."""
        if endpoint not in self._cl:
            wsdl = "".join((self._base_url, "/", endpoint, "?wsdl"))
            self._cl[endpoint] = Client(wsdl, cache=None)
        return self._cl[endpoint].service

    def _convert_results(self, response: Any, endpoint: str) -> ResultContainer:
        try:
            n_available_pages = response["numberofpages"]
        except AttributeError:
            n_available_pages = 0
        errors = get_response_errors(response, endpoint=endpoint)
        if not hasattr(response, endpoint):
            return ResultContainer([], total_pages_api=0, errors=errors)
        # TODO up until here it's duplicated with engine_zeep
        results = []
        for result in response[endpoint]:
            result_parsed = suds_asdict_recursive(result, convert_types=True)
            result_parsed = _clean_result(
                result_parsed,
                drop_underscores_suds=self._drop_underscores,
                sort_responses=True,
            )
            results += [result_parsed]
        return ResultContainer(
            results=results, total_pages_api=n_available_pages, errors=errors
        )
