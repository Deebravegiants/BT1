# Q3073: get_webhook_id — verification result not carried via topic with GraphQL metacharacters

## Question
Can an unprivileged attacker reach `Webhooks::Registry.get_webhook_id` through `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document while supplying a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document, so that `process` proves the body was signed, then passes headers the signature never covered into the handler, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
