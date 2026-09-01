# Q751: hmac — no replay protection via api-version header

## Question
Does `Webhooks::Request#hmac` collapse two distinct identities into one when an unprivileged attacker submits the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata` at `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header? Show that no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata`
- Exploit idea: no nonce, timestamp or delivery-id tracking bounds re-delivery of a signed body
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
