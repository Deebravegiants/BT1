# Q2809: register — tenant identity handed over unverified via mandatory topic names

## Question
Does `Webhooks::Registry.register` collapse two distinct identities into one when an unprivileged attacker submits one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic? Show that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
