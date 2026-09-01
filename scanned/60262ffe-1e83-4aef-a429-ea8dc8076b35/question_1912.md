# Q1912: initialize — guard order via tries argument

## Question
Starting from `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, can an unprivileged attacker supply a `tries:` value that lengthens the retry loop around an authenticated request so that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::Rest::Admin#initialize`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `tries:` value that lengthens the retry loop around an authenticated request
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
