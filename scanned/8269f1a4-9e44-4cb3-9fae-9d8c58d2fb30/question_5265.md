# Q5265: to_signable_string — presence check != usage via base64 padding variants

## Question
Starting from `to_signable_string`, which returns `@raw_body` and nothing else, can an unprivileged attacker supply an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops so that `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `Webhooks::Request#to_signable_string`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
