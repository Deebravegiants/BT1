# Q135: to_signable_string — lossy digest normalisation via own-shop signed body

## Question
Does `Webhooks::Request#to_signable_string` collapse two distinct identities into one when an unprivileged attacker submits a body validly signed for the attacker's own shop and replayed with different headers at `to_signable_string`, which returns `@raw_body` and nothing else? Show that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
