# Q5627: parsed_body — shop handed to handler unverified via relabelled shop header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain at `parsed_body`, a `JSON.parse(@raw_body)` performed after verification, makes `Webhooks::Request#parsed_body` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#parsed_body`
- Entrypoint: `parsed_body`, a `JSON.parse(@raw_body)` performed after verification
- Attacker controls: the `x-shopify-shop-domain` header, which no signature covers, set to a victim merchant's domain
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
