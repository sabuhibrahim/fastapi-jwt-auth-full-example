from .database import SessionFactory


async def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        await db.close()
