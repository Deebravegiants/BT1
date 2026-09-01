# Q1117: to_signable_string — no freshness via oversized hmac

## Question
Can an `hmac` value of a different length or casing than the hex digest `compute_signature` produces, supplied by an unprivileged attacker at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, make `AuthQuery#to_signable_string` and the code consuming its result disagree, given that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? The binding to test is BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on; the impact to prove is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an `hmac` value of a different length or casing than the hex digest `compute_signature` produces
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
