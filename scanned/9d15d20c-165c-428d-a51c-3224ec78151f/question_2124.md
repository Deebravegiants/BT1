# Q2124: register — GraphQL built by interpolation via replayed delivery

## Question
If an unprivileged attacker submits the same signed body and `webhook-id` delivered repeatedly to `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, does `Webhooks::Registry.register` end up acting on a value that was never authenticated, because topic and `webhook_id` are concatenated into query documents rather than passed as variables? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
