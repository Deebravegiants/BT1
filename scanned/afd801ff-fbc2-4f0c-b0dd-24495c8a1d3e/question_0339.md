# Q339: to_signable_string — signature covers body only via relabelled shop header

## Question
If an unprivileged attacker submits the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain to `to_signable_string`, which returns `@raw_body` and nothing else, does `Webhooks::Request#to_signable_string` end up acting on a value that was never authenticated, because `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `to_signable_string` returns `@raw_body`, so topic, shop, api-version and webhook-id are unauthenticated input travelling with a valid HMAC
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
