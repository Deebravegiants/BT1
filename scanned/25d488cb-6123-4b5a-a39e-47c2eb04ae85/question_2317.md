# Q2317: topic — handler chosen by unsigned data via base64 padding variants

## Question
Can an unprivileged attacker reach `Webhooks::Request#topic` through `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header while supplying an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops, so that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists, breaking the requirement that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
