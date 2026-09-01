# Q3348: register — GraphQL built by interpolation via unsigned shop header

## Question
Does `Webhooks::Registry.register` collapse two distinct identities into one when an unprivileged attacker submits the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop` at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic? Show that topic and `webhook_id` are concatenated into query documents rather than passed as variables, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop`
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
