# Q422: register — dispatch on unauthenticated data via unregistered topic

## Question
Does `Webhooks::Registry.register` collapse two distinct identities into one when an unprivileged attacker submits a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals at `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic? Show that the handler is selected by `request.topic`, a header the HMAC does not cover, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.register`
- Entrypoint: `Registry.register(topic:, session:)`, which builds and sends a GraphQL mutation for a topic
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
