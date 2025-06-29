from typing import Optional ,List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from models import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = TaskStatus.pending
    priority: Optional[TaskPriority] = TaskPriority.medium
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, max_length=100)

    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title must not be empty or whitespace.")
        return v.strip()

    @validator("due_date")
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Due date must be in the future.")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    due_date: Optional[datetime]
    assigned_to: Optional[str] = Field(None, max_length=100)

    @validator("title")
    def title_strip(cls, v):
        if v and not v.strip():
            raise ValueError("Title must not be empty or whitespace.")
        return v.strip()

    @validator("due_date")
    def due_date_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Due date must be in the future.")
        return v


class TaskResponse(TaskCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes  = True



class BulkUpdateRequest(BaseModel):
    task_ids: List[int]
    updates: TaskUpdate

class BulkDeleteRequest(BaseModel):
    task_ids: List[int]