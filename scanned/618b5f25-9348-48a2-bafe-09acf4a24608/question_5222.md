# Q5222: request_url — attacker-steered retry loop via response-driven retry

## Question
Can an unprivileged attacker reach `Clients::HttpClient#request_url` through the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation while supplying a 429 or 500 response with a chosen `retry-after` header, steering the retry loop, so that response headers decide how long and how often the authenticated request is repeated, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
