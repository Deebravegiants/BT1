# Q3884: request_url — caller headers win via traversal to another version

## Question
Is there a reachable state in which an unprivileged attacker, controlling `../<other version>/` segments that move the request to an API version the app did not configure at the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`, makes `Clients::Rest::Admin#request_url` return a result the caller treats as authenticated, given that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#request_url`
- Entrypoint: the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`
- Attacker controls: `../<other version>/` segments that move the request to an API version the app did not configure
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
