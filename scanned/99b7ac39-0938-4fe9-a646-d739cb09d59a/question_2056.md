# Q2056: to_signable_string — coverage gap via unsigned extra params

## Question
Trace `AuthQuery#to_signable_string` from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback with any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`: because a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
