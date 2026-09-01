# Q1951: to_signable_string — ambiguous concatenation via array-style parameters

## Question
Trace `AuthQuery#to_signable_string` from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback with `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new`: because two different parameter sets serialise to the same signable string, does the value that was verified stop being the value that is used? Prove the break against BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new`
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
