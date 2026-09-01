# Q3128: unregister — dispatch on unauthenticated data via topic with GraphQL metacharacters

## Question
Is there a reachable state in which an unprivileged attacker, controlling a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document at `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, makes `Webhooks::Registry.unregister` return a result the caller treats as authenticated, given that the handler is selected by `request.topic`, a header the HMAC does not cover? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: a topic containing quotes, braces or newlines that survive `gsub(%r{/|\.}, "_").upcase` into the query document
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
