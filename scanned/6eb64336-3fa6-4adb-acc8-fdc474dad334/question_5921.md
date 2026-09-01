# Q5921: to_signable_string — header collision via omitted optional headers

## Question
Is there a reachable state in which an unprivileged attacker, controlling an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String at `to_signable_string`, which returns `@raw_body` and nothing else, makes `Webhooks::Request#to_signable_string` return a result the caller treats as authenticated, given that two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: an omitted `x-shopify-api-version` or `x-shopify-webhook-id`, which `initialize` never requires but the accessors `T.cast` to String
- Exploit idea: two spellings of one logical header resolve differently in `initialize`'s presence check than in `shopify_header`'s lookup
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `Request#hmac` yields the same value for two different header strings, then assert `HmacValidator.validate` accepts both
