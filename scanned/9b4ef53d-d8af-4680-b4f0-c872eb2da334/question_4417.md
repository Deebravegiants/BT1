# Q4417: request_url — attacker-steered retry loop via path traversal segments

## Question
Can an unprivileged attacker reach `Clients::HttpClient#request_url` through the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation while supplying `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path, so that response headers decide how long and how often the authenticated request is repeated, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `X-Shopify-Access-Token` appears in no recorded request whose host is outside `TRUSTED_SHOPIFY_DOMAINS`
