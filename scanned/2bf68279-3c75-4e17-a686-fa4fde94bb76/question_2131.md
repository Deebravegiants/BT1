# Q2131: to_signable_string — canonicalisation gap via oversized hmac

## Question
If an unprivileged attacker submits an `hmac` value of a different length or casing than the hex digest `compute_signature` produces to `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, does `AuthQuery#to_signable_string` end up acting on a value that was never authenticated, because the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding? Close the question on BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an `hmac` value of a different length or casing than the hex digest `compute_signature` produces
- Exploit idea: the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
