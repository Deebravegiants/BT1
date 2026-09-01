# Q4875: topic — presence check != usage via base64 padding variants

## Question
If an unprivileged attacker submits an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops to `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, does `Webhooks::Request#topic` end up acting on a value that was never authenticated, because `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: an hmac header with altered padding, whitespace or non-alphabet characters that `Base64.decode64` silently drops
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
