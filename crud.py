from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime
from models import Task, TaskStatus, TaskPriority
from schemas import TaskCreate, TaskUpdate

class TaskCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(**task_data.dict())
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "asc"
    ) -> tuple[List[Task], int]:

        query = select(Task)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if search:
            query = query.where(
                Task.title.contains(search) | Task.description.contains(search)
            )

        # Apply sorting
        sort_column = getattr(Task, sort_by)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        query = query.order_by(sort_column)

        # Pagination
        query = query.offset(skip).limit(limit)

        tasks = self.session.exec(query).all()
        total = len(tasks)

        return tasks, total

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None

        update_data = task_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            for field, value in update_data.items():
                setattr(task, field, value)

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.session.get(Task, task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def get_tasks_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> tuple[List[Task], int]:
        return self.get_tasks(skip=skip, limit=limit, status=status)

    def get_tasks_by_priority(self, priority: TaskPriority, skip: int = 0, limit: int = 100) -> tuple[List[Task], int]:
        return self.get_tasks(skip=skip, limit=limit, priority=priority)
    
    
    
    def bulk_update_tasks(self, task_ids: List[int], update_data: TaskUpdate) -> List[Task]:
            updated_tasks = []
            update_dict = update_data.dict(exclude_unset=True)

            if not update_dict:
                return []

            for task_id in task_ids:
                task = self.session.get(Task, task_id)
                if task:
                    for field, value in update_dict.items():
                        setattr(task, field, value)
                    task.updated_at = datetime.utcnow()
                    self.session.add(task)
                    updated_tasks.append(task)

            self.session.commit()
            for task in updated_tasks:
                self.session.refresh(task)
            return updated_tasks


    