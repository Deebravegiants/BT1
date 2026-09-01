# Q4167: shopify_header — shop handed to handler unverified via own-shop signed body

## Question
Does `Webhooks::Request#shopify_header` collapse two distinct identities into one when an unprivileged attacker submits a body validly signed for the attacker's own shop and replayed with different headers at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`? Show that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
