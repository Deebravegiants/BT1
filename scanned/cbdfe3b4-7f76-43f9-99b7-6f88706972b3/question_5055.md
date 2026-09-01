# Q5055: to_signable_string — presence check != usage via own-shop signed body

## Question
Starting from `to_signable_string`, which returns `@raw_body` and nothing else, can an unprivileged attacker supply a body validly signed for the attacker's own shop and replayed with different headers so that `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Request#to_signable_string`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a body validly signed for the attacker's own shop and replayed with different headers
- Exploit idea: `initialize` only requires `topic`, `hmac-sha256` and `shop-domain` to exist, never that they are well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
