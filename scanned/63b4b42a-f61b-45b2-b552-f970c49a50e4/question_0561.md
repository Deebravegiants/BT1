# Q561: process — dispatch on unauthenticated data via unregistered topic

## Question
Starting from `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, can an unprivileged attacker supply a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals so that the handler is selected by `request.topic`, a header the HMAC does not cover? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Webhooks::Registry.process`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
