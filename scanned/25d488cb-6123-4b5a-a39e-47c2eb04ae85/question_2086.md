# Q2086: to_signable_string — coverage gap via encoding-sensitive values

## Question
Can an unprivileged attacker reach `AuthQuery#to_signable_string` through `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback while supplying values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing), so that a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes, breaking the requirement that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on, and ending in High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop?

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing)
- Exploit idea: a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a canonical query with the test secret, mutate an out-of-coverage field, and assert `validate` still returns true
