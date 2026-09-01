# Q1124: initialize — path built by interpolation via case-varied prefix

## Question
Can a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip, supplied by an unprivileged attacker at `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, make `Clients::Rest::Admin#initialize` and the code consuming its result disagree, given that resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
