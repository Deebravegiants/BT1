# Q2701: process — shared mutable registry via unsigned shop header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop` at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, makes `Webhooks::Registry.process` return a result the caller treats as authenticated, given that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the shop, taken from an unsigned header, handed to the handler as `WebhookMetadata#shop`
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
