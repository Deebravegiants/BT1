# Q133: to_signable_string — ambiguous concatenation via nil vs empty

## Question
Can an unprivileged attacker reach `AuthQuery#to_signable_string` through `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback while supplying an omitted parameter presented as an empty string, so the signable string still contains the key, so that two different parameter sets serialise to the same signable string, breaking the requirement that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an omitted parameter presented as an empty string, so the signable string still contains the key
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
