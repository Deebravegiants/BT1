# Q1974: unregister — verification result not carried via unregistered topic

## Question
Can an unprivileged attacker reach `Webhooks::Registry.unregister` through `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation while supplying a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals, so that `process` proves the body was signed, then passes headers the signature never covered into the handler, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: a topic with no handler, exercising the `NoWebhookHandler` path and what it reveals
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
