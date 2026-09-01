# Q798: initialize — header override ordering via path traversal segments

## Question
Can an unprivileged attacker reach `Clients::HttpClient#initialize` through `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token` while supplying `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path, so that `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
