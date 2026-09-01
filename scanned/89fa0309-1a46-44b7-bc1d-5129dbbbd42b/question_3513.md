# Q3513: add_registration — shared mutable registry via replayed delivery

## Question
Is there a reachable state in which an unprivileged attacker, controlling the same signed body and `webhook-id` delivered repeatedly at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, makes `Webhooks::Registry.add_registration` return a result the caller treats as authenticated, given that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
