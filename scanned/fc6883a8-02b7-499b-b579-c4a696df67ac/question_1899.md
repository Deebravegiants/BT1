# Q1899: add_registration — no replay tracking via unsigned topic header

## Question
Does `Webhooks::Registry.add_registration` collapse two distinct identities into one when an unprivileged attacker submits the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`? Show that no delivery-id or timestamp bookkeeping bounds re-delivery, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: no delivery-id or timestamp bookkeeping bounds re-delivery
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay one signed delivery twice and assert the handler is invoked at most once per `webhook-id`
