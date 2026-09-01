# Q517: register — GraphQL built by interpolation via mandatory topic names

## Question
Is there a reachable state in which an unprivileged attacker, controlling one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, makes `Webhooks::Registry.register` return a result the caller treats as authenticated, given that topic and `webhook_id` are concatenated into query documents rather than passed as variables? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
