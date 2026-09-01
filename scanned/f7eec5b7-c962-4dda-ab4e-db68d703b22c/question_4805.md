# Q4805: topic — no replay protection via relabelled shop header

## Question
If an unprivileged attacker submits the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain to `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, does `Webhooks::Request#topic` end up acting on a value that was never authenticated, because no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
