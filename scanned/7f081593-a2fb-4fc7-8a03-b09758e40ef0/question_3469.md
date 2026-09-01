# Q3469: add_registration — GraphQL built by interpolation via topic with GraphQL metacharacters

## Question
Can a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document, supplied by an unprivileged attacker at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, make `Webhooks::Registry.add_registration` and the code consuming its result disagree, given that topic and `webhook_id` are concatenated into query documents rather than passed as variables? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
