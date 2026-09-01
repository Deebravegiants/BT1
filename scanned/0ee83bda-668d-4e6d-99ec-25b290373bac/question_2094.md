# Q2094: add_registration — verification result not carried via unsigned topic header

## Question
Starting from `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`, can an unprivileged attacker supply the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents so that `process` proves the body was signed, then passes headers the signature never covered into the handler? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Webhooks::Registry.add_registration`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: `process` proves the body was signed, then passes headers the signature never covered into the handler
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
