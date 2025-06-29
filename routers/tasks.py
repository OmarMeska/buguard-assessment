from fastapi import APIRouter, HTTPException, Depends, Query , Body
from sqlmodel import Session
from typing import List, Optional

from models import Task
from schemas import BulkUpdateRequest, BulkDeleteRequest
from schemas import TaskCreate, TaskResponse, TaskUpdate, TaskStatus, TaskPriority
from database import get_session
from crud import TaskCRUD

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    return TaskCRUD(session).create_task(task)


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 10,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(default="created_at", enum=["created_at", "due_date", "priority"]),
    sort_order: Optional[str] = Query(default="asc", enum=["asc", "desc"])
):
    tasks, _ = TaskCRUD(session).get_tasks(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = TaskCRUD(session).get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/bulk-update", response_model=List[TaskResponse])
def bulk_update(
    data: BulkUpdateRequest ,
    session: Session = Depends(get_session)
):
    updated = TaskCRUD(session).bulk_update_tasks(data.task_ids, data.updates)
    if not updated:
        raise HTTPException(status_code=404, detail="No tasks updated")
    return updated


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, session: Session = Depends(get_session)):
    task = TaskCRUD(session).update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task






@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    deleted = TaskCRUD(session).delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": 1 }




@router.get("/status/{status}", response_model=List[TaskResponse])
def get_tasks_by_status(status: TaskStatus, session: Session = Depends(get_session)):
    tasks, _ = TaskCRUD(session).get_tasks_by_status(status)
    return tasks


@router.get("/priority/{priority}", response_model=List[TaskResponse])
def get_tasks_by_priority(priority: TaskPriority, session: Session = Depends(get_session)):
    tasks, _ = TaskCRUD(session).get_tasks_by_priority(priority)
    return tasks


