# Q2414: unregister — tenant identity handed over unverified via replayed delivery

## Question
Is there a reachable state in which an unprivileged attacker, controlling the same signed body and `webhook-id` delivered repeatedly at `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, makes `Webhooks::Registry.unregister` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
