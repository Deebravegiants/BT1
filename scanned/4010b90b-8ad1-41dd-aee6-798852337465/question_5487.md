# Q5487: shopify_header — lossy digest normalisation via api-version header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata` at the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`, makes `Webhooks::Request#shopify_header` return a result the caller treats as authenticated, given that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#shopify_header`
- Entrypoint: the private `shopify_header`, which prefers `shopify-<name>` over `x-shopify-<name>`
- Attacker controls: the unsigned `x-shopify-api-version` header, passed straight into `WebhookMetadata`
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
