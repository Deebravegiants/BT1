# Q5235: to_signable_string — shop handed to handler unverified via http_ prefix stripping

## Question
Is there a reachable state in which an unprivileged attacker, controlling a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key at `to_signable_string`, which returns `@raw_body` and nothing else, makes `Webhooks::Request#to_signable_string` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: a header literally named `http_shopify-topic`, whose `sub("http_","")` rewrite creates a second claimant for one key
- Exploit idea: `WebhookMetadata#shop` is the raw header value and is what the host app uses to decide whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
