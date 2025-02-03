import datetime as dt

from pydantic import BaseModel


class Job(BaseModel):
    job_title: str
    location: str

    @classmethod
    def from_string(cls, input_str: str):
        terms = input_str.split(",")
        if len(terms) != 2:
            raise ValueError(
                "Input must contain exactly one comma separating two terms"
            )
        return cls(job_title=terms[0].strip(), location=terms[1].strip())


class JobWithCount(Job):
    ts: dt.datetime
    count: int
