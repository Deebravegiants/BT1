# Q683: to_signable_string — type confusion via stale signed callback

## Question
Can an old but validly signed callback, since `timestamp` is carried into the signature yet never compared to now, supplied by an unprivileged attacker at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, make `AuthQuery#to_signable_string` and the code consuming its result disagree, given that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an old but validly signed callback, since `timestamp` is carried into the signature yet never compared to now
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
