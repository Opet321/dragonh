import environs


env = environs.Env()
env.read_env("./config.env")

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
bot_token = "7764544491:AAEuyGkR8DNvqLjktcb6CJlH2xpFKnENQpo"

session_string = env.str("SESSION_STRING", "")

db_url = env.str("MONGODB_URL", "mongodb+srv://apem:apem@cluster0.iraog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_name = "Dragon-Fork"

version = "[Selfbot] Dragon-Fork v1.1.0"
