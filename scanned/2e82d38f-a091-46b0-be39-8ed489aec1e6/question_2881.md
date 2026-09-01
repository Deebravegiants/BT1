# Q2881: process — shared mutable registry via replayed delivery

## Question
Can the same signed body and `webhook-id` delivered repeatedly, supplied by an unprivileged attacker at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, make `Webhooks::Registry.process` and the code consuming its result disagree, given that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
