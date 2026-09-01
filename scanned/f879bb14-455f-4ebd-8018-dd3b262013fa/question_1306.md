# Q1306: register — shared mutable registry via topic with GraphQL metacharacters

## Question
Can a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document, supplied by an unprivileged attacker at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, make `Webhooks::Registry.register` and the code consuming its result disagree, given that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
