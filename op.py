from abc import abstractmethod


class Operation:
    @property
    @abstractmethod
    def offset(self):
        return 0, 0

    @property
    @abstractmethod
    def idxs(self):
        return 0, 0


class Delete(Operation):
    def __init__(self, row_idx: int, col_idx: int, length: int):
        self.pos = (row_idx, col_idx)
        self._offset = (col_idx, -length)
        self._length = length

    @property
    def offset(self):
        return self.pos[1], -self._length

    @property
    def idxs(self):
        return self.pos

    @property
    def length(self):
        return self._length


class Insert(Operation):
    def __init__(self, row_idx: int, col_idx: int, text: str):
        self.pos = (row_idx, col_idx)
        self.text = text

    @property
    def offset(self):
        return self.pos[1], len(self.text)

    @property
    def idxs(self):
        return self.pos


class OP:
    operations: list[Operation]
    text: list[str]

    def __init__(self):
        self.text = ['']
        self.operations = [Operation()]

    def insert(self, version: int, row_idx: int, col_idx: int, text: str):
        true_pos = col_idx

        for i in range(version + 1, len(self.operations)):
            i = self.operations[i]
            if i.idxs[0] == row_idx and i.offset[0] <= true_pos:
                true_pos += i.offset[1]

        self.operations.append(Insert(row_idx, true_pos, text))

    def delete(self, version: int, row_idx: int, col_idx: int, length: int):
        true_pos = col_idx

        for i in range(version + 1, len(self.operations)):
            i = self.operations[i]
            if i.idxs[0] != row_idx:
                continue

            if isinstance(i, Insert):
                if i.offset[0] <= true_pos:
                    true_pos += i.offset[1]
            elif isinstance(i, Delete):
                # let ----- - old delete, ~~~~~ - new delete

                # when
                # ...~~~~~.... O ..~~~~~.. O ..~~~~~... O ...~~~~~~..
                # .---------.. R ..-----.. R ..-------. R .--------..
                if i.offset[0] <= true_pos and i.offset[0] + i.length >= true_pos + length:
                    self.operations.append(Delete(row_idx, true_pos, 0))
                    return

                # When
                # .------..... O .-----..... O ..----........
                # ...~~~~~~~.. R .~~~~~~~~.. R .....~~~~~~...
                if i.offset[0] <= true_pos and i.offset[0] + i.length > true_pos:
                    new_pos = i.offset[0] + i.length
                    length -= new_pos - true_pos
                    true_pos = new_pos - i.length
                # When
                # ...------... O ...--------..
                # .~~~~~~~~~~. R .~~~~~~~~~~..
                elif true_pos < i.offset[0] and i.offset[0] + i.length <= true_pos + length:
                    length -= i.length
                # ...------..
                # .~~~~~~....
                elif true_pos < i.offset[0] and i.offset[0] <= true_pos + length:
                    length -= true_pos + length - i.offset[0]
                # When
                # ..----......... O .........-----..
                # .......~~~~~~.. R ..~~~~~~........
                else:
                    if i.offset[0] <= true_pos:
                        true_pos += i.offset[1]

        self.operations.append(Delete(row_idx, true_pos, length))

    def sync(self):
        for i in self.operations:
            while i.idxs[0] >= len(self.text):
                self.text.append('')
            if isinstance(i, Insert):
                row_idx, col_idx = i.idxs
                self.text[row_idx] = self.text[row_idx][:col_idx] + i.text + self.text[row_idx][col_idx:]
            elif isinstance(i, Delete):
                row_idx, col_idx = i.idxs
                self.text[row_idx] = self.text[row_idx][:col_idx] + self.text[row_idx][col_idx + i.length:]

        self.operations.clear()
        self.operations.append(Operation())

    def pre(self):
        text = self.text.copy()
        for i in self.operations:
            while i.idxs[0] >= len(text):
                text.append('')
            if isinstance(i, Insert):
                row_idx, col_idx = i.idxs
                text[row_idx] = text[row_idx][:col_idx] + i.text + text[row_idx][col_idx:]
            elif isinstance(i, Delete):
                row_idx, col_idx = i.idxs
                text[row_idx] = text[row_idx][:col_idx] + text[row_idx][col_idx + i.length:]
        return text
