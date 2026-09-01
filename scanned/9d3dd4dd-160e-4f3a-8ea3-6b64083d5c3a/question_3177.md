# Q3177: shopify_header — verified bytes != parsed bytes via base64 padding variants

## Question
Is there a reachable state in which an unprivileged attacker, controlling an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, makes `Webhooks::Request#shopify_header` return a result the caller treats as authenticated, given that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
