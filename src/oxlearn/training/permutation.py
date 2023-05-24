from collections.abc import Container as _Container


class Permutation:
    _instances: dict[tuple[int, ...], "Permutation"] = {}

    @classmethod
    def cycle(cls, *args: tuple[int, ...]) -> "Permutation":
        return Permutation(
            *tuple(
                args[(args.index(i) + 1) % len(args)] if i in args else i
                for i in range(9)
            )
        )

    _mapping: tuple[int, int, ...]

    def __new__(cls, *mapping: tuple[int, ...]) -> "Permutation":
        sanitized_mapping = list(mapping)
        while sanitized_mapping and sanitized_mapping[-1] == len(sanitized_mapping) - 1:
            sanitized_mapping.pop()
        sanitized_mapping = tuple(sanitized_mapping)
        if sanitized_mapping in cls._instances:
            return cls._instances[sanitized_mapping]
        inst = super(Permutation, cls).__new__(cls)
        inst._mapping = sanitized_mapping
        cls._instances[sanitized_mapping] = inst
        return inst

    def __mul__(
        self, other: "int | _Container | Permutation | None"
    ) -> "int | _Container | Permutation | None":
        if isinstance(other, int):
            return self._mapping[other] if other < len(self._mapping) else other
        if isinstance(other, _Container):
            return type(other)(other[self * i] for i in range(len(other)))
        if isinstance(other, Permutation):
            return Permutation(*(self * other.extended_mapping(len(self.mapping))))
        if other is None:
            return None
        raise TypeError

    def __invert__(self) -> "Permutation":
        return Permutation(
            *tuple(self._mapping.index(i) for i in sorted(self._mapping))
        )

    def _cycle_decomposition(self) -> tuple[tuple[int, ...]]:
        cycles = []
        counted = []
        for n in range(len(self._mapping)):
            if n not in counted:
                cycle = [n]
                i = self * n
                while i != n:
                    cycle.append(i)
                    i = self * i
                if len(cycle) > 1:
                    cycles.append(tuple(cycle))
                counted.extend(cycle)
        return tuple(cycles)

    @property
    def cycles(self) -> tuple[int, ...]:
        cycles = self._cycle_decomposition()
        return tuple(self.cycle(*cycle) for cycle in cycles)

    @property
    def mapping(self) -> tuple[int, ...]:
        return self._mapping

    def extended_mapping(self, n_elements: int) -> tuple[int, ...]:
        mapping_ext = self.mapping
        if len(mapping_ext) < n_elements:
            mapping_ext += tuple(range(len(mapping_ext), n_elements))
        return mapping_ext

    def __str__(self) -> str:
        return str(self.mapping)
        cycles = self._cycle_decomposition()
        if cycles:
            return " * ".join(
                "(" + " ".join(str(n) for n in cycle) + ")" for cycle in cycles
            )
        else:
            return "()"

    def __repr__(self) -> str:
        return f"Permutation{self._mapping}"
