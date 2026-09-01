# Q2593: unregister — tenant identity handed over unverified via webhook_id from a response

## Question
If an unprivileged attacker submits a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string to `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, does `Webhooks::Registry.unregister` end up acting on a value that was never authenticated, because `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
