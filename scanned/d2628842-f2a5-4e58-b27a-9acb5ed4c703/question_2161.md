# Q2161: to_signable_string — ambiguous concatenation via unsigned extra params

## Question
Trace `AuthQuery#to_signable_string` from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback with any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`: because two different parameter sets serialise to the same signable string, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
