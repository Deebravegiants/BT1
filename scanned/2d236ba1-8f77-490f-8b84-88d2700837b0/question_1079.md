# Q1079: to_signable_string — coverage gap via host param

## Question
Starting from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, can an unprivileged attacker supply the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin so that a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `AuthQuery#to_signable_string`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: a field the host app or gem acts on is outside `to_signable_string`, so a valid HMAC vouches for less than the app assumes
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
