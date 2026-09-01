# Q5888: to_signable_string — verified bytes != parsed bytes via own-shop signed body

## Question
Starting from `to_signable_string`, which returns `@raw_body` and nothing else, can an unprivileged attacker supply a body validly signed for the attacker's own shop and replayed with different headers so that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Request#to_signable_string`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
