# Q755: serialized_error — attacker-steered retry loop via path traversal segments

## Question
Is there a reachable state in which an unprivileged attacker, controlling `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path at `serialized_error`, which builds an error message from response body and headers, makes `Clients::HttpClient#serialized_error` return a result the caller treats as authenticated, given that response headers decide how long and how often the authenticated request is repeated? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
