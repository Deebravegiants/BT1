# Q2343: parsed_body — presence check != usage via relabelled topic header

## Question
Trace `Webhooks::Request#parsed_body` from `parsed_body`, a `JSON.parse(@raw_body)` performed after verification with the `x-shopify-topic` header, which selects the handler in `Registry.process`: because `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: the `x-shopify-topic` header, which selects the handler in `Registry.process`
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
