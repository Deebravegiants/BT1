# Q2032: make_request — guard order via body-type coupling

## Question
Does `Clients::Rest::Admin#make_request` collapse two distinct identities into one when an unprivileged attacker submits a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify` at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`? Show that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify`
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
