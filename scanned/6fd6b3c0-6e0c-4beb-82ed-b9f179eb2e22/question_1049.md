# Q1049: get_webhook_id — dispatch on unauthenticated data via webhook_id from a response

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string at `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document, makes `Webhooks::Registry.get_webhook_id` return a result the caller treats as authenticated, given that the handler is selected by `request.topic`, a header the HMAC does not cover? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: a `webhook_id` taken from an upstream response and interpolated directly into the delete mutation string
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
