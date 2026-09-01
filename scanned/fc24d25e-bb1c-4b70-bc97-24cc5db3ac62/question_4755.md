# Q4755: parsed_body — signature covers body only via relabelled shop header

## Question
Does `Webhooks::Request#parsed_body` collapse two distinct identities into one when an unprivileged attacker submits the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification? Show that `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
