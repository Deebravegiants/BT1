# Q4785: shopify_header — handler chosen by unsigned data via replayed webhook-id

## Question
Can a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids, supplied by an unprivileged attacker at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, make `Webhooks::Request#shopify_header` and the code consuming its result disagree, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
