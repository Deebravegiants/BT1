# Q823: add_registration — mandatory-topic short-circuit via replayed delivery

## Question
Can the same signed body and `webhook-id` delivered repeatedly, supplied by an unprivileged attacker at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, make `Webhooks::Registry.add_registration` and the code consuming its result disagree, given that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
