# Q4026: register — dispatch on unauthenticated data via registry mutation timing

## Question
Starting from `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic, can an unprivileged attacker supply concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash so that the handler is selected by `request.topic`, a header the HMAC does not cover? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Registry.register`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
