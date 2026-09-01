# Q5: hmac — no replay protection via http_ prefix stripping

## Question
Trace `Webhooks::Request#hmac` from `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header with a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key: because no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
