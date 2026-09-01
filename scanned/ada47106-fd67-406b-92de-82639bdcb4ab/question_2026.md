# Q2026: to_signable_string — no freshness via unsigned extra params

## Question
If an unprivileged attacker submits any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp` to `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, does `AuthQuery#to_signable_string` end up acting on a value that was never authenticated, because nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
