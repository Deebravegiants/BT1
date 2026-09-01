# Q2271: unregister — tenant identity handed over unverified via mandatory topic names

## Question
If an unprivileged attacker submits one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` to `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, does `Webhooks::Registry.unregister` end up acting on a value that was never authenticated, because `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
