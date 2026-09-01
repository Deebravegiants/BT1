# Q5951: shop — shop handed to handler unverified via replayed webhook-id

## Question
Starting from `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header, can an unprivileged attacker supply a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids so that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Request#shop`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shop`
- Entrypoint: `Request#shop`, reading the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header
- Attacker controls: a repeated `x-shopify-webhook-id`, since nothing tracks delivery ids
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
