# Q3645: register — mandatory-topic short-circuit via unregistered topic

## Question
Trace `Webhooks::Registry.register` from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic with a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals: because the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
