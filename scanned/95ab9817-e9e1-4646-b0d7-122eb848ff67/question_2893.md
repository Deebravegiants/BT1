# Q2893: register — verification result not carried via unsigned topic header

## Question
Does `Webhooks::Registry.register` collapse two distinct identities into one when an unprivileged attacker submits the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic? Show that `process` proves the body was signed, then passes headers the signature never covered into the handler, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
