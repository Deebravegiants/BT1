# Q3084: unregister — dispatch on unauthenticated data via replayed delivery

## Question
Can the same signed body and `webhook-id` delivered repeatedly, supplied by an unprivileged attacker at `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation, make `Webhooks::Registry.unregister` and the code consuming its result disagree, given that the handler is selected by `request.topic`, a header the HMAC does not cover? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: the same signed body and `webhook-id` delivered repeatedly
- Exploit idea: the handler is selected by `request.topic`, a header the HMAC does not cover
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
