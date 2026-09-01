# Q1297: initialize — type confusion via delimiter injection

## Question
Does `AuthQuery#initialize` collapse two distinct identities into one when an unprivileged attacker submits a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous at `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string? Show that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it, that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
