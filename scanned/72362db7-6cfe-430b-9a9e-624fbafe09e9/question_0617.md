# Q617: to_signable_string — canonicalisation gap via nil vs empty

## Question
Starting from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, can an unprivileged attacker supply an omitted parameter presented as an empty string, so the signable string still contains the key so that the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `AuthQuery#to_signable_string`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an omitted parameter presented as an empty string, so the signable string still contains the key
- Exploit idea: the string reconstructed by `URI.encode_www_form` is not byte-identical to what Shopify signed, so verification depends on incidental encoding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
