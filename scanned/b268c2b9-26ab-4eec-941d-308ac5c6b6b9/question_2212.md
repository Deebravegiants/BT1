# Q2212: make_request — path built by interpolation via case-varied prefix

## Question
Can an unprivileged attacker reach `Clients::Rest::Admin#make_request` through the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers` while supplying a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip, so that resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
