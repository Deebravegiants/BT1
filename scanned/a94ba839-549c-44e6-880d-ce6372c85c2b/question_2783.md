# Q2783: initialize — guard order via api_version override

## Question
Can an `api_version:` argument derived from request input, changing the base path and the loaded resource classes, supplied by an unprivileged attacker at `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, make `Clients::Rest::Admin#initialize` and the code consuming its result disagree, given that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: an `api_version:` argument derived from request input, changing the base path and the loaded resource classes
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
