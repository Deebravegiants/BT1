# Q3227: get_webhook_id — shared mutable registry via mandatory topic names

## Question
Can an unprivileged attacker reach `Webhooks::Registry.get_webhook_id` through `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document while supplying one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`, so that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
