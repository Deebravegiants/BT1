# Q3496: to_signable_string — header collision via relabelled shop header

## Question
If an unprivileged attacker submits the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain to `to_signable_string`, which returns `@raw_body` and nothing else, does `Webhooks::Request#to_signable_string` end up acting on a value that was never authenticated, because two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: sign one body with the test secret, POST it twice with different `x-shopify-shop-domain` values, assert the handler receives two different shops for one signature
