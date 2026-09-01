# Q5015: topic — lossy digest normalisation via own-shop signed body

## Question
If an unprivileged attacker submits a body validly signed for the attacker's own shop and replayed with different headers to `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header, does `Webhooks::Request#topic` end up acting on a value that was never authenticated, because `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#topic`
- Entrypoint: `Request#topic`, reading the unsigned `shopify-topic` / `x-shopify-topic` header
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
