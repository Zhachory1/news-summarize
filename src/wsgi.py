from src import create_app

if __name__ == "__main__":
    create_app("src.conf.ProductionConfig").run(host="0.0.0.0")