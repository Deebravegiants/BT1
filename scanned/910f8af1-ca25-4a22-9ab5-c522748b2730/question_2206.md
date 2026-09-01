# Q2206: initialize — ambiguous concatenation via unicode normalisation

## Question
Starting from `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, can an unprivileged attacker supply a value that normalises differently between the browser, the framework and `URI.encode_www_form` so that two different parameter sets serialise to the same signable string? Determine whether BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on still holds through `AuthQuery#initialize`, and whether the result reaches High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: a value that normalises differently between the browser, the framework and `URI.encode_www_form`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
