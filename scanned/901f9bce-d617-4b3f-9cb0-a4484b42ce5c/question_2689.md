# Q2689: unregister — no replay tracking via unregistered topic

## Question
Starting from `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, can an unprivileged attacker supply a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals so that no delivery-id or timestamp bookkeeping bounds re-delivery? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Webhooks::Registry.unregister`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: no delivery-id or timestamp bookkeeping bounds re-delivery
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
