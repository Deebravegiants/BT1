# Q2349: unregister — tenant identity handed over unverified via registry mutation timing

## Question
Can concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash, supplied by an unprivileged attacker at `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, make `Webhooks::Registry.unregister` and the code consuming its result disagree, given that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
