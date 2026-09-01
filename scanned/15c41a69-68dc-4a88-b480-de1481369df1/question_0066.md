# Q66: unregister — shared mutable registry via unregistered topic

## Question
If an unprivileged attacker submits a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals to `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, does `Webhooks::Registry.unregister` end up acting on a value that was never authenticated, because `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
