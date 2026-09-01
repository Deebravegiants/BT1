# Q1234: add_registration — tenant identity handed over unverified via replayed delivery

## Question
Does `Webhooks::Registry.add_registration` collapse two distinct identities into one when an unprivileged attacker submits the same signed body and `webhook-id` delivered repeatedly at `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`? Show that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
