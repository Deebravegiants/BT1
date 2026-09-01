# Q2401: process — mandatory-topic short-circuit via mandatory topic names

## Question
Can an unprivileged attacker reach `Webhooks::Registry.process` through `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route while supplying one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`, so that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
