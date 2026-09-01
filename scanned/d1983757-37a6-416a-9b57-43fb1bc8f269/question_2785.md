# Q2785: process — tenant identity handed over unverified via mandatory topic names

## Question
Is there a reachable state in which an unprivileged attacker, controlling one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, makes `Webhooks::Registry.process` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
