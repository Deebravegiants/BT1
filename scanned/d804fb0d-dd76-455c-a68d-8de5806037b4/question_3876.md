# Q3876: unregister — mandatory-topic short-circuit via mandatory topic names

## Question
Trace `Webhooks::Registry.unregister` from `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation with one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`: because the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.unregister`
- Entrypoint: `Registry.unregister(topic:, session:)`, which interpolates a `webhook_id` into a delete mutation
- Attacker controls: one of `shop/redact`, `customers/redact`, `customers/data_request`, which short-circuit `register`/`unregister`
- Exploit idea: the `MANDATORY_TOPICS` check runs before any other validation and returns a success-shaped result
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: register two handlers, submit one signed body with each topic header, and assert dispatch follows the signature rather than the header
