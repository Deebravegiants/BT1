# Q5587: initialize — no replay protection via relabelled topic header

## Question
Starting from `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, can an unprivileged attacker supply the `x-shopify-topic` header, which selects the handler in `Registry.process` so that no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Request#initialize`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: the `x-shopify-topic` header, which selects the handler in `Registry.process`
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
