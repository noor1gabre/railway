import os
from typing import Optional
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 1. Database Setup
# Railway sometimes gives 'postgres://', but SQLAlchemy needs 'postgresql://'
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

# 2. Define the Table (Model)
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    description: Optional[str] = None

# 3. Create Tables on Startup
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Initialize App
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# 5. API Endpoints
@app.get("/")
def home():
    return {"status": "Online", "db": "Connected"}

@app.post("/products/")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

@app.get("/products/")
def read_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products