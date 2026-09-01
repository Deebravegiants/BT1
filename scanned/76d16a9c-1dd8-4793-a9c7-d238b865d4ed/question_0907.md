# Q907: process — dispatch on unauthenticated data via webhook_id from a response

## Question
Can a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string, supplied by an unprivileged attacker at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, make `Webhooks::Registry.process` and the code consuming its result disagree, given that the handler is selected by `request.topic`, a header the HMAC does not cover? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
