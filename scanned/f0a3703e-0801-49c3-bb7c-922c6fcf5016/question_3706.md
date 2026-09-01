# Q3706: add_registration — shared mutable registry via unsigned topic header

## Question
If an unprivileged attacker submits the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents to `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, does `Webhooks::Registry.add_registration` end up acting on a value that was never authenticated, because `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
