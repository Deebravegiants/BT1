# Q2011: initialize — coverage gap via nil vs empty

## Question
Does `AuthQuery#initialize` collapse two distinct identities into one when an unprivileged attacker submits an omitted parameter presented as an empty string, so the signable string still contains the key at `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string? Show that a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes, that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: an omitted parameter presented as an empty string, so the signable string still contains the key
- Exploit idea: a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
