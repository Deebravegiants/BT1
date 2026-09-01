# Q5753: shopify_header — handler chosen by unsigned data via duplicate header prefixes

## Question
Is there a reachable state in which an unprivileged attacker, controlling both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, makes `Webhooks::Request#shopify_header` return a result the caller treats as authenticated, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
