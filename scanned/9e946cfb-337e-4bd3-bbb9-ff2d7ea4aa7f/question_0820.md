# Q820: get — guard order via path prefix admin/

## Question
Starting from `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, can an unprivileged attacker supply a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely so that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::Rest::Admin#get`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
