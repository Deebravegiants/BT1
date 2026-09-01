# Q969: get_webhook_id — no replay tracking via topic with GraphQL metacharacters

## Question
If an unprivileged attacker submits a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document to `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document, does `Webhooks::Registry.get_webhook_id` end up acting on a value that was never authenticated, because no delivery-id or timestamp bookkeeping bounds re-delivery? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: no delivery-id or timestamp bookkeeping bounds re-delivery
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
