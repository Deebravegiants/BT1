# Q2665: register — shared mutable registry via registry mutation timing

## Question
Trace `Webhooks::Registry.register` from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic with concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash: because `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
