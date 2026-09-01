# Q5891: topic — signature covers body only via own-shop signed body

## Question
Can a body validly signed for the attacker's own shop and replayed with different headers, supplied by an unprivileged attacker at `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, make `Webhooks::Request#topic` and the code consuming its result disagree, given that `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
