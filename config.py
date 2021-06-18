#python -m venv <folder>
#pip install -r requirement.txt
import os 

class Config:

	def __init__(self):

		self.DB_PLATFORM = "postgresql"
		self.DB_SERVER = "localhost"
		self.DB_NAME = "noteapp"
		self.DB_USERNAME = "postgres"#os.getenv("DB_USERNAME")
		self.DB_PASSWORD = "postgre86"#os.getenv("DB_PASSWORD")

		self.SECRET_KEY = 'Ini Harusnya Rahasia'

		self.DB_URL=f"{self.DB_PLATFORM}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_SERVER}/{self.DB_NAME}" #WINDOWS
		#self.DB_URL=f"{self.DB_PLATFORM}://{self.DB_SERVER}/{self.DB_NAME}"

	def check_env(self):
		print(self.DB_USERNAME, self.DB_PASSWORD)

if __name__ == '__main__':
	myConfig = Config()
	myConfig.check_env()

