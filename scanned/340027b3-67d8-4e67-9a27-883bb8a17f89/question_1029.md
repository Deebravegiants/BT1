# Q1029: add_registration — dispatch on unauthenticated data via unregistered topic

## Question
Can an unprivileged attacker reach `Webhooks::Registry.add_registration` through `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)` while supplying a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals, so that the handler is selected by `request.topic`, a header the HMAC does not cover, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
