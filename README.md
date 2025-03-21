# Flats screener

## Idea

The app currently holds a scraper for [ss.lv](https://www.ss.com) public flats ads. The general configuration can be found in the config.toml file, while sensitive variables are declared in `.env` file:

```
TELEGRAM_USER_ID = "<YOUR_TELEGRAM_USER_ID>"
TELEGRAM_TOKEN = "<YOUR_TELEGRAM_TOKEN>"
POSTGRES_USER = "<POSTGRES_DB_USER>"
POSTGRES_PASSWORD = "<POSTGRES_DB_PASSWORD>"
POSTGRES_PORT = <POSTGRES_PORT>
POSTGRES_DB = <POSTGRES_DB>
```

At the moment cron jobs are set to run at 9,12,15,18 and 21, but can be changed if needed. When cron is triggered, the scraper crawls flat ads for the periods specified by `timeframe` field and deal type `deal_type` field and city `city_name` field in the `config.toml`, then filters out ads based on criteria specified under districts `[districts]` in the `config.toml` file. Afterwards filtered ads are added to the Postgres database. Prices are stored separetely to hold a history of price updates (linked by a custom id). Also, there is a separate table for favorite flats. Lastly, flats are sent to user's Telegram chat and can be added/removed from favorites in there by typing clicking a respective buttons. Favorites an be seen by sending `/favorites` massage to the chat. Along with message thumbnails are sent to the chat.

---

TODO:

- [ ] rename docker images
- [ ] Test renting case
- [ ] How can I handle user registration and filters submission?
- [ ] Add deal type to database docuemnts
- [ ] Create a cron for Postgres database dump
- [ ] Use free ratating proxies to spread requests
- [ ] Add zip.lv scraper
- [ ] Add mm.lv scraper
- [ ] Add varianti.lv scraper
- [ ] Create a separate task to populate locations for SS scraper
