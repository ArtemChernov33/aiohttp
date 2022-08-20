import json

from aiohttp import web
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = web.Application()
PG_DSN = 'postgresql+asyncpg://postgres:postgres@127.0.0.1/app'
engine = create_async_engine(PG_DSN, echo=True)
Base = declarative_base()

class HttpError(web.HTTPException):
    def __init__(self, *, headers=None, reason=None, body=None, message=None):
        json_response = json.dump({"error": message})
        super().__init__(
            headers=headers,
            reason=reason,
            body=body,
            text=json_response,
            content_type="application/json",
        )

class BadRequests(HttpError):
    status_code = 400

class NotFound(HttpError):
    status_code = 400


class Mail(Base):

    __tablename__ = 'mails'
    id = Column(Integer, primary_key=True)
    header = Column(String, nullable=False)
    description = Column(String, nullable=False)
    sender = Column(String, nullable=True)
    date_creation = Column(DateTime, server_default=func.now())

async def get_mail(mail_id: int, session) -> Mail:
    mail = await session.get(Mail, mail_id)
    if not mail:
        raise NotFound(message='mail not found')
    return mail



class MailView(web.View):
    async def get(self):
        mail_id = int(self.request.match_info["mail_id"])
        async with app.async_session_maker() as session:
            # mail_id = await session.get(Mail, mail_id)
            mail = await get_mail(mail_id, session)
            return web.json_response({
                'header': mail.header,
                'date_creation': int(mail.date_creation.timestamp()),
            }
            )

    async def post(self):
        mail_data = await self.request.json()
        new_mail = Mail(**mail_data)
        async with app.async_session_maker() as session:
            try:
                session.add(new_mail)
                await session.commit()
                return web.json_response({'id': new_mail.id})
            except IntegrityError as er:
                raise BadRequests(message="mail already exist")

    async def patch(self):
        mail_id  = int(self.request.match_info["mail_id"])
        mail_data = await self.request.json()
        async with app.async_session_maker() as session:
            mail = await get_mail(mail_id, session)
            for column, value in mail_data.items():
                setattr(mail, column, value)
            session.add(mail)
            await session.commit()
        return web.json_response({"status": "all okay"})

    async def delete(self):
        mail_id = int(self.request.match_info["mail_id"])
        async with app.async_session_maker() as session:
            mail = await get_mail(mail_id, session)
            await session.delete(mail)
            await session.commit()
            return web.json_response({'status': 'succes'})

async def init_orm(app: web.Application):
    print("Старт")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async_session_maker = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        app.async_session_maker = async_session_maker
        yield
    print("Конец")

app.cleanup_ctx.append(init_orm)
app.add_routes([web.get("/mails/{mail_id:\d+}", MailView)])
app.add_routes([web.patch("/mails/{mail_id:\d+}", MailView)])
app.add_routes([web.delete("/mails/{mail_id:\d+}", MailView)])
app.add_routes([web.post("/mails/", MailView)])


web.run_app(app)