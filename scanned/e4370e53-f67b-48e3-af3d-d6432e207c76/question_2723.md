# Q2723: request_url — path built by interpolation via double .json

## Question
Can an unprivileged attacker reach `Clients::Rest::Admin#request_url` through the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/` while supplying a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite, so that resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#request_url`
- Entrypoint: the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
