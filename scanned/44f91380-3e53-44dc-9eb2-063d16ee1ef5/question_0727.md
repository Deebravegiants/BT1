# Q727: to_signable_string — type confusion via nil vs empty

## Question
Is there a reachable state in which an unprivileged attacker, controlling an omitted parameter presented as an empty string, so the signable string still contains the key at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, makes `AuthQuery#to_signable_string` return a result the caller treats as authenticated, given that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it? Test BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an omitted parameter presented as an empty string, so the signable string still contains the key
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
