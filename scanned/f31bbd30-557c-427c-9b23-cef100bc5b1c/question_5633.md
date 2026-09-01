# Q5633: shop — shop handed to handler unverified via duplicate JSON keys

## Question
Trace `Webhooks::Request#shop` from `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header with a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins: because `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a body containing a repeated JSON key, where the signed bytes and the `JSON.parse` result disagree about which value wins
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
