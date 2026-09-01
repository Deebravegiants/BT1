# Q2926: initialize — attacker-steered retry loop via extra_headers

## Question
Can an unprivileged attacker reach `Clients::HttpClient#initialize` through `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token` while supplying `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`, so that response headers decide how long and how often the authenticated request is repeated, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
