# Q2747: post — path built by interpolation via traversal to another version

## Question
If an unprivileged attacker submits `../<other version>/` segments that move the request to an API version the app did not configure to `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token, does `Clients::Rest::Admin#post` end up acting on a value that was never authenticated, because resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#post`
- Entrypoint: `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token
- Attacker controls: `../<other version>/` segments that move the request to an API version the app did not configure
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
