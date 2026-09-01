# Q2505: unregister — GraphQL built by interpolation via replayed delivery

## Question
Is there a reachable state in which an unprivileged attacker, controlling the same signed body and `webhook-id` delivered repeatedly at `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, makes `Webhooks::Registry.unregister` return a result the caller treats as authenticated, given that topic and `webhook_id` are concatenated into query documents rather than passed as variables? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
