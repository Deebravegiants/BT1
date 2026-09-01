# Q4985: topic — header collision via duplicate JSON keys

## Question
Starting from `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, can an unprivileged attacker supply a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins so that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `Webhooks::Request#topic`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
