# Q3326: register — mandatory-topic short-circuit via unsigned topic header

## Question
Starting from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, can an unprivileged attacker supply the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents so that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Registry.register`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
