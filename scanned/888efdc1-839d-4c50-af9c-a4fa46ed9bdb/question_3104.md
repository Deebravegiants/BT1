# Q3104: get — path built by interpolation via api_version override

## Question
If an unprivileged attacker submits an `api_version:` argument derived from request input, changing the base path and the loaded resource classes to `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, does `Clients::Rest::Admin#get` end up acting on a value that was never authenticated, because resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: an `api_version:` argument derived from request input, changing the base path and the loaded resource classes
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
