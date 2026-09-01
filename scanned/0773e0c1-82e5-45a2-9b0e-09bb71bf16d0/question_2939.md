# Q2939: get — prefix re-rooting via double .json

## Question
Is there a reachable state in which an unprivileged attacker, controlling a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite at `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, makes `Clients::Rest::Admin#get` return a result the caller treats as authenticated, given that the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
