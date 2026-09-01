# Q5185: to_signable_string — handler chosen by unsigned data via omitted optional headers

## Question
Trace `Webhooks::Request#to_signable_string` from `to_signable_string`, which returns `@raw_body` and nothing else with an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String: because `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String
- Exploit idea: `Registry.process` dispatches on `request.topic` before any per-topic authorisation exists
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
