# Q1427: to_signable_string — no freshness via host param

## Question
Is there a reachable state in which an unprivileged attacker, controlling the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, makes `AuthQuery#to_signable_string` return a result the caller treats as authenticated, given that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
