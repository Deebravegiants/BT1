# Q623: request_url — header override ordering via path traversal segments

## Question
Can an unprivileged attacker reach `Clients::HttpClient#request_url` through the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation while supplying `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path, so that `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
