# Q2073: shop — signature covers body only via omitted optional headers

## Question
Starting from `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, can an unprivileged attacker supply an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String so that `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `Webhooks::Request#shop`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
