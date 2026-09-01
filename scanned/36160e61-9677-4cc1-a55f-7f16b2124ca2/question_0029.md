# Q29: to_signable_string — ambiguous concatenation via delimiter injection

## Question
Starting from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, can an unprivileged attacker supply a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous so that two different parameter sets serialise to the same signable string? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `AuthQuery#to_signable_string`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: a `code`, `state` or `host` value containing `&` or `=` so the concatenated signable string is ambiguous
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
