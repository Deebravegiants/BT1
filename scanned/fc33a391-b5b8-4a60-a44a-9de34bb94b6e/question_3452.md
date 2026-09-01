# Q3452: shopify_header — verified bytes != parsed bytes via http_ prefix stripping

## Question
Starting from the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, can an unprivileged attacker supply a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key so that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Request#shopify_header`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
