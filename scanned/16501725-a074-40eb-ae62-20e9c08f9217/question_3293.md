# Q3293: add_registration — tenant identity handed over unverified via topic with GraphQL metacharacters

## Question
If an unprivileged attacker submits a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document to `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, does `Webhooks::Registry.add_registration` end up acting on a value that was never authenticated, because `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `WebhookMetadata#shop` cannot differ from a shop authenticated by the request
