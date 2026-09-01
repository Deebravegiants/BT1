# Q1972: request_url — version chosen per call via path prefix admin/

## Question
Trace `Clients::Rest::Admin#request_url` from the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/` with a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely: because the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#request_url`
- Entrypoint: the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`
- Attacker controls: a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely
- Exploit idea: the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
