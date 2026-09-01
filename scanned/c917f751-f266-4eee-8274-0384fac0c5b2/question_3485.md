# Q3485: topic — header collision via replayed webhook-id

## Question
Is there a reachable state in which an unprivileged attacker, controlling a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids at `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, makes `Webhooks::Request#topic` return a result the caller treats as authenticated, given that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
