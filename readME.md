# Automatizations

Do you need automatization or even web developer? Contact me via email 4419970@gmail.com

# Problem/Fix

At Evermart (online platform that sell courses) the customer can't cancel their signature after subscriped in a product yet. After the charge on credit card the customer sometimes call us asking to cancel their membership and refund, so what I did was create a Telegram Bot that my Support Customer has access inputs the user signature e-mail and later will cancel the signature on Evermart.

# Configuration

- Modify the file `config.sample.json` to `config.json`
- Create a Bot on Telegram and edit the `config.json` at Key `telegram_bot` with your Bot informations
- Add your Bot in a group chat.
- Block your Bot on Bot Father Settings to be allowed to be added in others Groups, and remove the privacy mode in Bot Father settings as well.
- Done! =)

# Requirements

You need to store your sales (order and customer) in a database, and has an API Route that will receive a `GET Method` with the email and returns the last order transaction for this e-mail. The order transaction that is checked is the key `transaction` on Evermart Webhooks Array. You must configure teh API route in the file `config.json` as well.

Sample:

Method GET = `https://api.teste.com/lastorder/4419970@gmail.com`
Returns:

```json
{
  "code": "123456789"
}
```
