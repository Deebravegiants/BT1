# Q2146: initialize — coverage gap via unicode normalisation

## Question
Can a value that normalises differently between the browser, the framework and `URI.encode_www_form`, supplied by an unprivileged attacker at `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, make `AuthQuery#initialize` and the code consuming its result disagree, given that a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: a value that normalises differently between the browser, the framework and `URI.encode_www_form`
- Exploit idea: a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
