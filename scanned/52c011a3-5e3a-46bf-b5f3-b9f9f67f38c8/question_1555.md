# Q1555: initialize — no freshness via unsigned extra params

## Question
Starting from `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, can an unprivileged attacker supply any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp` so that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `AuthQuery#initialize`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
