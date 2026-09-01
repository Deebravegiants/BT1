# Q1173: hmac — verified bytes != parsed bytes via base64url vs standard

## Question
Can a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets, supplied by an unprivileged attacker at `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header, make `Webhooks::Request#hmac` and the code consuming its result disagree, given that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
