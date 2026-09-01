# Q2963: register — shared mutable registry via replayed delivery

## Question
Does `Webhooks::Registry.register` collapse two distinct identities into one when an unprivileged attacker submits the same signed body and `webhook-id` delivered repeatedly at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic? Show that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
