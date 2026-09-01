# Q2638: serialized_error — mutable shared header hash via path traversal segments

## Question
Is there a reachable state in which an unprivileged attacker, controlling `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path at `serialized_error`, which builds an error message from response body and headers, makes `Clients::HttpClient#serialized_error` return a result the caller treats as authenticated, given that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
