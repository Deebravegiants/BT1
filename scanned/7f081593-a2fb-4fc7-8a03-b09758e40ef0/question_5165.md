# Q5165: shop — lossy digest normalisation via relabelled shop header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain at `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, makes `Webhooks::Request#shop` return a result the caller treats as authenticated, given that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
