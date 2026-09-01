# Q485: shopify_header — header collision via duplicate JSON keys

## Question
Does `Webhooks::Request#shopify_header` collapse two distinct identities into one when an unprivileged attacker submits a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`? Show that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup, that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
