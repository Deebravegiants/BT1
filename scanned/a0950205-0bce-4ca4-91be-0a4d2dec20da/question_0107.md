# Q107: to_signable_string — type confusion via unsigned extra params

## Question
Does `AuthQuery#to_signable_string` collapse two distinct identities into one when an unprivileged attacker submits any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp` at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback? Show that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: any query parameter the app reads that is not one of `code`, `host`, `shop`, `state`, `timestamp`
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
