# Q5420: topic — handler chosen by unsigned data via duplicate JSON keys

## Question
Does `Webhooks::Request#topic` collapse two distinct identities into one when an unprivileged attacker submits a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins at `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header? Show that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
