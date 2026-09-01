# Q2362: get_webhook_id — GraphQL built by interpolation via registry mutation timing

## Question
If an unprivileged attacker submits concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash to `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document, does `Webhooks::Registry.get_webhook_id` end up acting on a value that was never authenticated, because topic and `webhook_id` are concatenated into query documents rather than passed as variables? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.get_webhook_id`
- Entrypoint: `get_webhook_id(topic:, client:)`, which interpolates `topic.gsub(%r{/|\.}, "_").upcase` into a GraphQL document
- Attacker controls: concurrent `add_registration`/`clear` against `process`, since `@registry` is a plain class-level hash
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
