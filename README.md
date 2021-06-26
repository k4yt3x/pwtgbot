# pwtgbot

PwnWiki Telegram database searching bot.

## Screenshots

![image](https://user-images.githubusercontent.com/21986859/123431975-654ad080-d5b9-11eb-89f3-23f13db54d1c.png)\
*How it looks like in the terminal when running*

![image](https://user-images.githubusercontent.com/21986859/123431912-519f6a00-d5b9-11eb-8b54-834fb571923b.png)\
*How it looks like in Telegram*

## Run Directly From Source

```shell
# clone and enter repository
git clone https://github.com/k4yt3x/pwtgbot.git
cd pwtgbot

# set Telegram bot token
export PWTGBOT_SECRET="TELEGRAM BOT SECRET"

# launch bot
python -m pwtgbot
```

## Run With Docker/Podman

You can run this bot from its Docker image.

- `$PWTGBOT_SECRET`: Telegram bot secret token
- `$VERSION_TAG`: pwtgbot version (e.g., 1.2.0)
	- You can check out the newest tag on [Docker Hub](https://hub.docker.com/r/k4yt3x/pwtgbot)

```shell
# add Telegram bot token as secret
echo $PWTGBOT_SECRET | podman secret create pwtgbot -

# launch docker container
docker run -it --name pwtgbot --secret pwtgbot docker.io/k4yt3x/pwtgbot:$VERSION_TAG
```

## Building the Docker Image

```shell
# clone and enter repository
git clone https://github.com/k4yt3x/pwtgbot.git
cd pwtgbot

# build the image
docker build -t pwtgbot:latest .
```

## License

Due to management issues, this program is now licensed under a proprietary license. You must read and agree to the [EULA](LICENSE) prior to using this program. Should you need to modify or redistribute the source code, please contact the author for exclusive permissions.
