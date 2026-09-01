# Q551: to_signable_string — no single-use via delimiter injection

## Question
Trace `AuthQuery#to_signable_string` from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback with a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous: because nothing marks a signed callback as consumed, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous
- Exploit idea: nothing marks a signed callback as consumed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
