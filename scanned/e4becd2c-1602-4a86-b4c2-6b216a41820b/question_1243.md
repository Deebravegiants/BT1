# Q1243: initialize — no single-use via encoding-sensitive values

## Question
Can values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing), supplied by an unprivileged attacker at `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, make `AuthQuery#initialize` and the code consuming its result disagree, given that nothing marks a signed callback as consumed? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing)
- Exploit idea: nothing marks a signed callback as consumed
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
