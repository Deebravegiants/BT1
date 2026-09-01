# Q1191: hmac — shop handed to handler unverified via duplicate header prefixes

## Question
Starting from `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header, can an unprivileged attacker supply both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order so that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Request#hmac`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
