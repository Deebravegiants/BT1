# Q3194: process — shared mutable registry via topic with GraphQL metacharacters

## Question
Does `Webhooks::Registry.process` collapse two distinct identities into one when an unprivileged attacker submits a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route? Show that `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: `@registry` is process-global and mutable at runtime, so what a topic maps to can change between verification and dispatch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
