import main


def lambda_handler(event, context):
    main.handler()
    return {"statusCode": 200}


if __name__ == "__main__":
    lambda_handler('event', 'context')
