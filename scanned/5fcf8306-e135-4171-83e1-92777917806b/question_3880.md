# Q3880: parsed_body — handler chosen by unsigned data via underscore/dash aliasing

## Question
Does `Webhooks::Request#parsed_body` collapse two distinct identities into one when an unprivileged attacker submits header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic` at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification? Show that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
