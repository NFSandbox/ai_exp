from dataclasses import dataclass, replace
from collections.abc import Set, Sequence
from copy import deepcopy


class InvalidMoveDirection(Exception):
    pass


def count_inversions(arr):
    inversions = 0
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                inversions += 1
    return inversions


class EFPState:
    def __init__(
        self,
        sequence: list[int],
        end_state: "EFPState | None" = None,
        update_distance: bool = True,
    ) -> None:
        self.matrix: list[list[int]] = [
            sequence[0:3],
            sequence[3:6],
            sequence[6:9],
        ]
        self.distance_to_end: int = -1
        self.end_state = end_state
        self.prev_state: "EFPState | None" = None

        if update_distance:
            self.update_distance_to_end()

    def update_distance_to_end(self):
        if self.end_state is not None:
            self.distance_to_end = self.distance(self.end_state)
        else:
            self.distance_to_end = -1

    def __hash__(self):
        return tuple(self.to_sequence()).__hash__()

    def __eq__(self, value: object) -> bool:
        return value.__hash__() == self.__hash__()

    def to_sequence(self) -> list[int]:
        sequence: list[int] = []
        for row in self.matrix:
            sequence.extend(row)

        return sequence

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int):
        self.matrix[key[0]][key[1]] = value

    def visualize(self) -> str:
        repr_str = ""
        for row in self.matrix:

            for n in row:
                # repr_str += " "
                if n == 0:
                    repr_str += " "
                else:
                    repr_str += str(n)
                repr_str += " "

            repr_str += "\n"

        return repr_str[:-1]  # remove \n at the end

    def get_index(self, value: int):
        """
        Get a 2-dim index of a value in the matrix.
        """
        for i in range(0, 3):
            for j in range(0, 3):
                if self.matrix[i][j] == value:
                    return (i, j)

        raise RuntimeError(f"Could not find index of number {value}")

    def distance(self, other: "EFPState") -> int:
        distance = 0
        for i in range(3):
            for j in range(3):
                value = self.matrix[i][j]
                if value == 0:
                    continue

                coor = other.get_index(value)
                distance += abs(coor[1] - j)
                distance += abs(coor[0] - i)

        return distance

    def extend(self) -> list["EFPState"]:
        extended_states: list["EFPState"] = []

        try:
            extended_states.append(self.__copy__().move(l=True))
        except InvalidMoveDirection:
            pass

        try:
            extended_states.append(self.__copy__().move(r=True))
        except InvalidMoveDirection:
            pass

        try:
            extended_states.append(self.__copy__().move(u=True))
        except InvalidMoveDirection:
            pass

        try:
            extended_states.append(self.__copy__().move(d=True))
        except InvalidMoveDirection:
            pass

        for st in extended_states:
            st.prev_state = self

        return extended_states

    def swap(self, coor1: tuple[int, int], coor2: tuple[int, int]):
        tmp = self[coor1]
        self[coor1] = self[coor2]
        self[coor2] = tmp
        self.update_distance_to_end()

    def move(
        self, l: bool = False, r: bool = False, u: bool = False, d: bool = False
    ) -> "EFPState":
        """
        Move a number in the matrix.
        """

        zero_index = self.get_index(0)
        if l:
            if zero_index[1] == 0:
                raise InvalidMoveDirection("Can't move left.")
            self.swap(zero_index, (zero_index[0], zero_index[1] - 1))

        elif r:
            if zero_index[1] == 2:
                raise InvalidMoveDirection("Can't move right.")
            self.swap(zero_index, (zero_index[0], zero_index[1] + 1))
        elif u:
            if zero_index[0] == 0:
                raise InvalidMoveDirection("Can't move up.")
            self.swap(zero_index, (zero_index[0] - 1, zero_index[1]))
            # move up
            pass
        elif d:
            if zero_index[0] == 2:
                raise InvalidMoveDirection("Can't move down.")
            self.swap(zero_index, (zero_index[0] + 1, zero_index[1]))
            pass
        else:
            raise RuntimeError("No direction given.")
        return self

    def __copy__(self):
        newst = EFPState(self.to_sequence(), self.end_state, update_distance=False)
        newst.distance_to_end = self.distance_to_end

        return newst


def a_sharp_search(start: EFPState, end: EFPState):
    start.distance_to_end = start.distance(end)
    start.end_state = end

    inversion_diff = count_inversions(start.to_sequence()) - count_inversions(
        end.to_sequence()
    )

    if inversion_diff % 2 != 0:
        raise RuntimeError("Different inversion pairs parity, no solution.")

    visited: dict[EFPState, bool] = {}
    process_list: list[EFPState] = [start]

    while process_list is not None:
        process_list.sort(key=lambda x: x.distance_to_end)
        current_state = process_list.pop(0)
        if visited.get(current_state, False):
            continue
        visited[current_state] = True

        if current_state == end:
            return current_state

        process_list.extend(current_state.extend())


def main():
    end_st = EFPState([1, 2, 3, 4, 5, 0, 7, 8, 6])
    start_st = EFPState([8, 3, 5, 4, 1, 0, 2, 6, 7], end_st)

    res = a_sharp_search(start_st, end_st)

    while res is not None:
        print(res.visualize())
        print("-----")
        res = res.prev_state


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
