# Q5684: topic — verified bytes != parsed bytes via base64url vs standard

## Question
Can an unprivileged attacker reach `Webhooks::Request#topic` through `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header while supplying a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets, so that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical, breaking the requirement that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
