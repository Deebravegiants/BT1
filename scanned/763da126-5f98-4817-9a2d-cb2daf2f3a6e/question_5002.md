# Q5002: request_url — dev-mode rewrite in production via base_path argument

## Question
Can the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation, supplied by an unprivileged attacker at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, make `Clients::HttpClient#request_url` and the code consuming its result disagree, given that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
