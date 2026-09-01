# Q2034: get_webhook_id — tenant identity handed over unverified via topic with GraphQL metacharacters

## Question
Can a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document, supplied by an unprivileged attacker at `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document, make `Webhooks::Registry.get_webhook_id` and the code consuming its result disagree, given that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
