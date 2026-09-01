# Q4880: to_signable_string — no replay protection via relabelled shop header

## Question
Starting from `to_signable_string`, which returns `@raw_body` and nothing else, can an unprivileged attacker supply the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain so that no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Request#to_signable_string`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
