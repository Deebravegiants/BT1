# Q627: process — GraphQL built by interpolation via unsigned shop header

## Question
Can the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop`, supplied by an unprivileged attacker at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, make `Webhooks::Registry.process` and the code consuming its result disagree, given that topic and `webhook_id` are concatenated into query documents rather than passed as variables? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop`
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
