# Q2611: initialize — header collision via base64url vs standard

## Question
Can an unprivileged attacker reach `Webhooks::Request#initialize` through `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST while supplying a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets, so that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#initialize`
- Entrypoint: `Request.new(raw_body:, headers:)`, called by the app's public webhook endpoint on every inbound POST
- Attacker controls: a base64url-encoded digest (`-`/`_`) that `decode64` reinterprets
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
