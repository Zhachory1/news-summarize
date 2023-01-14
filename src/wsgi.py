from src import create_app

if __name__ == "__main__":
    create_app("src.conf.DevelopmentConfig").run(host="0.0.0.0")