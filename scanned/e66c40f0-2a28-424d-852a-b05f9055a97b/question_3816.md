# Q3816: register — tenant identity handed over unverified via unsigned shop header

## Question
Starting from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, can an unprivileged attacker supply the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop` so that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Registry.register`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop`
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
