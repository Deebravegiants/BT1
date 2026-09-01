# Q3331: initialize — handler chosen by unsigned data via api-version header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata` at `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST, makes `Webhooks::Request#initialize` return a result the caller treats as authenticated, given that `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata`
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
