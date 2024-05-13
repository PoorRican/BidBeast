from typing import Optional, Iterator
from uuid import UUID

from langchain.pydantic_v1 import BaseModel


class Job(BaseModel):
    id: Optional[UUID]
    title: str
    description: str
    link: str

    def __repr__(self):
        return self.title

    def summary_repr(self, index: Optional[int] = None) -> str:
        prefix = '##'
        if index is not None:
            prefix += f" {index+1}."
        return f"{prefix} {self.title}\n\n{self.link}"

    def detailed_repr(self) -> Iterator[str]:
        yield f"\n\n# {self.title}\n"

        # divide description into chunks of 2000 characters
        chunk_len = 2000
        for i in range(0, len(self.description), chunk_len):
            yield f"\n{self.description[i:i + chunk_len]}"
