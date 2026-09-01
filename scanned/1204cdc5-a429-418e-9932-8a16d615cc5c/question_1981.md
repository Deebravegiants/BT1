# Q1981: initialize — no freshness via host param

## Question
Can an unprivileged attacker reach `AuthQuery#initialize` through `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string while supplying the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin, so that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely, breaking the requirement that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
