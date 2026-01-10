import os

# 1. Database
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Security
SECRET_KEY = "07fbc1b851e6aff8b50c8c7902859366"  # غير دي ضروري
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# 3. Cloudflare R2 Keys (حط مفاتيحك اللي اشتغلت هنا)
R2_ACCOUNT_ID = "1fc8fb2e1a931161faa604bb1dbab8b7"
R2_ACCESS_KEY_ID = "73a823150346bdf1946e7b6a4f6a9aac"
R2_SECRET_ACCESS_KEY = "7fff51048bbeb44c91a373ff1ccb546ed3ca4f5558d1412ea9e02cb128ce6719"
R2_BUCKET_NAME = "products"
R2_PUBLIC_DOMAIN = "https://pub-9d8e69f9b5e6474d90bccbed1591bca8.r2.dev"
