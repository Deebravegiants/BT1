# Q1715: to_signable_string — canonicalisation gap via host param

## Question
Can an unprivileged attacker reach `AuthQuery#to_signable_string` through `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback while supplying the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin, so that the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
