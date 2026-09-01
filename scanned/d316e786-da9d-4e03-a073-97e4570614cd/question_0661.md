# Q661: initialize — ambiguous concatenation via array-style parameters

## Question
If an unprivileged attacker submits `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new` to `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, does `AuthQuery#initialize` end up acting on a value that was never authenticated, because two different parameter sets serialise to the same signable string? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
