# Q2019: process — verification result not carried via replayed delivery

## Question
If an unprivileged attacker submits the same signed body and `webhook-id` delivered repeatedly to `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, does `Webhooks::Registry.process` end up acting on a value that was never authenticated, because `process` proves the body was signed, then passes headers the signature never covered into the handler? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
