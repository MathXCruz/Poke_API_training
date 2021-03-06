import logging
import asyncio
import httpx
from typing import List


def get_info(endpoint: str, id_or_name: str) -> dict:
    """Return a dictionary of the PokeAPI data.

    Args:
        endpoint (str): The endpoint to query, endpoints can be found on
        https://pokeapi.co/docs/v2.
        id_or_name (str): The id or name of the PokeThing you want data for.

    Returns:
        dict: The raw data of the pokemon.
    """
    url = f'https://pokeapi.co/api/v2/{endpoint}/{id_or_name}'
    response = httpx.get(url)
    logging.info(f'get_data(poke_api): {response.status_code}')
    return response.json()


async def get_pokemon_data(min_id: int, max_id: int) -> List[dict]:
    """Return a dict list of data of the Pokemon in the min_id to max_id - 1 range.

    Args:
        min_id (int): The id of the first pokemon you want data for.
        max_id (int): The id of the last pokemon you want data for.

    Returns:
        dict: The raw data of every requested pokemon.
    """
    reqs = [create_request(ID) for ID in range(min_id, max_id)]
    poke_list = await get_pokemon(reqs)
    pokemon = [p.json() for p in poke_list]
    return pokemon


def create_request(ID: int) -> httpx.Request:
    """Create a get request for the given ID.

    Args:
        ID (int): The id of the pokemon you want data for.

    Returns:
        httpx.Request: The request to get the data for the pokemon.
    """
    return httpx.Request('GET', url=f'https://pokeapi.co/api/v2/pokemon/{ID}')


async def get_pokemon(reqs: List[httpx.Request]) -> List[httpx.Response]:
    """Create a client and manage the creation and execution of the requests.

    Args:
        reqs (List[httpx.Request]): A list of requests to make.

    Returns:
        List[httpx.Response]: A list of responses from the requests.
    """
    limits = httpx.Limits(max_connections=30, max_keepalive_connections=30)
    timeout = httpx.Timeout(60)
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        tasks = [client.send(req) for req in reqs]
        return await asyncio.gather(*tasks)


def get_pokemon_data_sync(min_id: int, max_id: int) -> list:
    """Return a dict of data from the (min_id)th to the (max_id)th - 1 Pokemon.

    Uses Synchronous requests.

    Args:
        min_id (int): The id of the first pokemon you want data for.
        max_id (int): The id of the last pokemon you want data for.

    Returns:
        list: A list containing the raw data of every requested pokemon.
    """
    pkmn = []
    with httpx.Client() as client:
        for id in range(min_id, max_id):
            url = f'https://pokeapi.co/api/v2/pokemon/{id}'
            response = client.get(url)
            logging.debug(f'get_async_data(poke_api): {response.status_code}')
            pkmn.append(response.json())
    return pkmn
