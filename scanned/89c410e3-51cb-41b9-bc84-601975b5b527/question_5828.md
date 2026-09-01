# Q5828: hmac — handler chosen by unsigned data via underscore/dash aliasing

## Question
Can header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`, supplied by an unprivileged attacker at `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header, make `Webhooks::Request#hmac` and the code consuming its result disagree, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
