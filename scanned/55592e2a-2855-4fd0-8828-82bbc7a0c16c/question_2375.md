# Q2375: add_registration — tenant identity handed over unverified via webhook_id from a response

## Question
Does `Webhooks::Registry.add_registration` collapse two distinct identities into one when an unprivileged attacker submits a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`? Show that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
