# Q1279: initialize — ambiguous concatenation via unsigned extra params

## Question
Trace `AuthQuery#initialize` from `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string with any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`: because two different parameter sets serialise to the same signable string, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
