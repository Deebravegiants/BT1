# Q3359: process — dispatch on unauthenticated data via mandatory topic names

## Question
Is there a reachable state in which an unprivileged attacker, controlling one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, makes `Webhooks::Registry.process` return a result the caller treats as authenticated, given that the handler is selected by `request.topic`, a header the HMAC does not cover? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
