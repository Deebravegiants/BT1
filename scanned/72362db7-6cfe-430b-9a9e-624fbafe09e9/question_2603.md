# Q2603: post — path built by interpolation via case-varied prefix

## Question
Is there a reachable state in which an unprivileged attacker, controlling a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip at `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token, makes `Clients::Rest::Admin#post` return a result the caller treats as authenticated, given that resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#post`
- Entrypoint: `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token
- Attacker controls: a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
