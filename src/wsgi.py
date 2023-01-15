from src import create_app

# TODO(zhach): Add flag to switch between dev, prod, and test
if __name__ == "__main__":
    create_app("src.conf.ProductionConfig").run(host="0.0.0.0")