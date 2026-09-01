# Q4980: topic — presence check != usage via duplicate header prefixes

## Question
If an unprivileged attacker submits both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order to `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, does `Webhooks::Request#topic` end up acting on a value that was never authenticated, because `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
