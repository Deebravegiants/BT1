# Q1324: process — mandatory-topic short-circuit via topic with GraphQL metacharacters

## Question
Starting from `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, can an unprivileged attacker supply a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document so that the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Webhooks::Registry.process`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
