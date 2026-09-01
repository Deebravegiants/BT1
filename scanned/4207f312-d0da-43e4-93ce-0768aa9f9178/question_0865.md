# Q865: register — mandatory-topic short-circuit via replayed delivery

## Question
Can the same signed body and `webhook-id` delivered repeatedly, supplied by an unprivileged attacker at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, make `Webhooks::Registry.register` and the code consuming its result disagree, given that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
