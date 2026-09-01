# Q3746: unregister — dispatch on unauthenticated data via mandatory topic names

## Question
Starting from `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, can an unprivileged attacker supply one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister` so that the handler is selected by `request.topic`, a header the HMAC does not cover? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Registry.unregister`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
