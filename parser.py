import re
from datetime import time
from typing import Any, Iterator


class ZTMParser:
    def __init__(self, path: str) -> None:
        self.path = path

    def parse_all(self) -> tuple[dict[int, dict[str, Any]], dict[str, dict[str, Any]]]:
        return self.parse_stop_groups(), self.parse_lines()

    def parse_lines(self) -> dict[str, dict[str, Any]]:
        lines = {}
        for record in (record_iterator := self.iterate_section("LL")):
            if not re.match(r"Linia:", record):
                continue
            line_identifier, line_params = ZTMParser.parse_line(record)
            lines[line_identifier] = line_params
            last_route_identifier = None
            last_transit_params = None
            for record in self.iterate_section("WK", record_iterator):
                route_identifier, transit_params = ZTMParser.parse_transit(record)
                if (
                    last_route_identifier is None
                    or route_identifier != last_route_identifier
                ):
                    last_route_identifier = route_identifier
                else:
                    transit_params["start_stop_number"] = last_transit_params[
                        "end_stop_number"
                    ]
                    transit_params["start_stop_time"] = last_transit_params[
                        "end_stop_time"
                    ]
                    transit_params["start_stop_attribute"] = last_transit_params[
                        "end_stop_attribute"
                    ]
                    lines[line_identifier].setdefault("routes", {}).setdefault(
                        route_identifier, []
                    ).append(transit_params)
                last_transit_params = transit_params
        return lines

    @staticmethod
    def parse_transit(record: str) -> tuple[str, dict[str, Any]]:
        values = ZTMParser.split_record(record, n_spaces=1)
        route_identifier = values[0]
        params = {
            "end_stop_number": int(values[1]),
            "running_day_type_symbol": values[2],
            "end_stop_time": ZTMParser.parse_time(values[3]),
            "end_stop_attribute": values[4] if len(values) == 5 else None,
        }
        return route_identifier, params

    @staticmethod
    def parse_time(value: str) -> time:
        hour, minute = map(int, re.split(r"\.", value))
        return time(hour % 24, minute)

    @staticmethod
    def parse_line(record: str) -> tuple[str, dict[str, Any]]:
        values = ZTMParser.split_record(record, n_spaces=2)
        if re.match(r"Linia:\s\w+", values[0]):
            values = re.split(r"\s", values[0]) + values[1:]
        identifier = values[1]
        params = {"type": ZTMParser.parse_line_type(values[2])}
        return identifier, params

    @staticmethod
    def parse_line_type(value: str) -> str:
        return re.match(r"-\s(.+)", value)[1].lower()

    def parse_stop_groups(self) -> dict[int, dict[str, Any]]:
        stop_groups = {}
        for record in (record_iterator := self.iterate_section("ZP")):
            if not re.match(r"\d{4}", record):
                continue
            stop_group_number, stop_group_params = ZTMParser.parse_stop_group(record)
            stop_groups[stop_group_number] = stop_group_params
            for record in self.iterate_section("PR", record_iterator):
                if re.match(r"\d{6}", record):
                    stop_number, stop_params = self.parse_stop(record)
                    stop_groups[stop_group_number].setdefault("stops", {})[
                        stop_number
                    ] = stop_params
                elif re.match(r"L", record):
                    stop_type, line_identifiers = self.parse_stop_lines(record)
                    stop_groups[stop_group_number]["stops"][stop_number].setdefault(
                        "lines", {}
                    )[stop_type] = line_identifiers
        return stop_groups

    @staticmethod
    def parse_stop_lines(record: str) -> tuple[str, list[str]]:
        values = ZTMParser.split_record(record, n_spaces=2)
        if re.match(r"L\s\d+", values[0]):
            values = re.split(r"\s", values[0]) + values[1:]
        stop_type = ZTMParser.parse_stop_type(values[2])
        line_identifiers = ZTMParser.parse_line_identifiers(values[3:])
        return stop_type, line_identifiers

    @staticmethod
    def parse_line_identifiers(values: list[str]) -> list[str]:
        return list({re.sub(r"\^", "", value) for value in values})

    @staticmethod
    def parse_stop_type(value: str) -> str:
        return re.match(r"-\s(.+):", value)[1]

    @staticmethod
    def parse_stop(record: str) -> tuple[int, dict[str, Any]]:
        values = ZTMParser.split_record(record, n_spaces=2)
        number = int(values[0])
        params = {
            "street": ZTMParser.parse_street(values[2]),
            "direction": ZTMParser.parse_direction(values[3]),
            "latitude": ZTMParser.parse_latitude(values[4]),
            "longitude": ZTMParser.parse_longitude(values[5]),
        }
        return number, params

    @staticmethod
    def parse_longitude(value: str) -> str:
        return (
            float(match[1]) if (match := re.match(r"X=\s(\d+\.\d+)", value)) else None
        )

    @staticmethod
    def parse_latitude(value: str) -> str:
        return (
            float(match[1]) if (match := re.match(r"Y=\s(\d+\.\d+)", value)) else None
        )

    @staticmethod
    def parse_direction(value: str) -> str:
        return ZTMParser.remove_comma(re.sub(r"Kier.:\s", "", value))

    @staticmethod
    def parse_street(value: str) -> str:
        return ZTMParser.remove_comma(re.sub(r"Ul./Pl.:\s", "", value))

    @staticmethod
    def parse_stop_group(record: str) -> tuple[int, dict[str, Any]]:
        values = ZTMParser.split_record(record, n_spaces=2)
        number = int(values[0])
        params = {
            "name": ZTMParser.remove_comma(values[1]),
            "locality_symbol": values[2],
            "locality_name": values[3].title(),
        }
        return number, params

    @staticmethod
    def remove_comma(value: str) -> str:
        return re.sub(r",$", "", value)

    @staticmethod
    def split_record(record: str, n_spaces: int) -> list[str]:
        return re.split(rf"\s{{{n_spaces},}}", record)

    def iterate_section(
        self, section_symbol: str, record_iterator: Iterator[str] | None = None
    ) -> Iterator[str]:
        close_iterator = False
        if record_iterator is None:
            record_iterator = open(self.path, encoding="cp1250")
            close_iterator = True
        inside_section = False
        for record in record_iterator:
            if re.match(rf"\s*\*{section_symbol}", record):
                inside_section = True
            elif re.match(rf"\s*#{section_symbol}", record):
                break
            elif inside_section:
                yield record.strip()
        if close_iterator:
            record_iterator.close()
