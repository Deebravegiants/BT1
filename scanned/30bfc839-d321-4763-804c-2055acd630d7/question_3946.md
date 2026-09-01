# Q3946: add_registration — mandatory-topic short-circuit via mandatory topic names

## Question
Trace `Webhooks::Registry.add_registration` from `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)` with one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`: because the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.add_registration`
- Entrypoint: `add_registration(topic:, delivery_method:, path:, handler:, fields:, filter:, metafield_namespaces:)`
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
