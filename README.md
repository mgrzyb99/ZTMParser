### Usage example:

```python
from parser import ZTMParser

parser = ZTMParser("path/to/data")
stop_groups, lines = parser.parse_all()
```

Recommended Python version is `>= 3.11`.

### Data structure:

- `stop_groups` (`dict`) - dictionary with `stop_group_number` (`int`, e.g. `1001`) as keys and dictionaries of the following structure as values:
    - `name` (`str`, e.g. `'Kijowska'`) - name of the stop group,
    - `locality_name` (`str`, e.g. `'Warszawa'`) - name of the locality in which the stop group is located,
    - `locality_symbol` (`str`, e.g. `'--'`) - symbol of the locality in which the stop group is located,
    - `stops` (`dict`) - dictionary with `stop_number` (`int`, e.g. `100101`) as keys and dictionaries of the following structure as values:
        - `street` (`str`, e.g. `'Targowa'`) - name of the street on which the stop is located,
        - `direction` (`str`, e.g. `'al. Zieleniecka'`) - general direction of the stop,
        - `latitude` (`float | None`, e.g. `52.248455`) - geographical latitude of the stop,
        - `longitude` (`float | None`, e.g. `21.044827`) - geographical longitude of the stop,
        - `lines` (`dict`) - dictionary with `stop_type` (`str`, e.g. `'stały'`) as values and `line_identifiers` (`list[str]`, e.g. `['102', '123', '125', ...]`) as values,
- `lines` (`dict`) - dictionary with `line_identifier` (`str`, e.g. `'1'`) as keys and dictionaries of the following structure as values:
    - `type` (`str`, e.g. `'linia tramwajowa'`) - type of the line,
    - `routes` (`dict`) - dictionary with `route_identifier` (`str`, e.g. `'TD-1AN03/DP/04.23'`) as keys and lists of dictionaries (called `transit`) of the following structure as values:
        - `start_stop_number` (`int`, e.g. `500403`) - number of the stop at which the transit starts,
        - `start_stop_time` (`datetime.time`, e.g. `datetime.time(4, 24)`) - time at which the transit starts,
        - `start_stop_attribute` (`str | None`, e.g. `'B'`) - additional attribute of the stop at which the transit starts,
        - `end_stop_number` (`int`, e.g. `500308`) - number of the stop at which the transit ends,
        - `end_stop_time` (`datetime.time(4, 27)`) - time at which the transit ends,
        - `end_stop_attribute` (`str | None`, e.g. `None`) - additional attribute of the stop at which the transit ends,
        - `running_day_type_symbol` (`str`, e.g. `'DP'`) - symbol of the day type at which the transit runs.

For more details see the [official ZTM documentation](https://www.ztm.waw.pl/wp-content/uploads/2014/04/1200_zasady.pdf).
