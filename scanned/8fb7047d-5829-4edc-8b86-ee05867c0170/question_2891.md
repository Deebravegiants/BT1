# Q2891: initialize — guard order via case-varied prefix

## Question
Can an unprivileged attacker reach `Clients::Rest::Admin#initialize` through `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch while supplying a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip, so that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
