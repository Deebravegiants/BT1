# Q3183: register — verification result not carried via webhook_id from a response

## Question
Trace `Webhooks::Registry.register` from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic with a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string: because `process` proves the body was signed, then passes headers the signature never covered into the handler, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
