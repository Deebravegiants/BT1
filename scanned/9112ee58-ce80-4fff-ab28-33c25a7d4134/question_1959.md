# Q1959: process — mandatory-topic short-circuit via unsigned topic header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, makes `Webhooks::Registry.process` return a result the caller treats as authenticated, given that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
