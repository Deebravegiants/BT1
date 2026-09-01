# Q3766: unregister — dispatch on unauthenticated data via unsigned topic header

## Question
Can an unprivileged attacker reach `Webhooks::Registry.unregister` through `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation while supplying the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents, so that the handler is selected by `request.topic`, a header the HMAC does not cover, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
