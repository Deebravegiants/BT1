# Q3763: serialized_error — mutable shared header hash via session.shop

## Question
Can `session.shop`, which for several flows was never passed through `ShopValidator`, supplied by an unprivileged attacker at `serialized_error`, which builds an error message from response body and headers, make `Clients::HttpClient#serialized_error` and the code consuming its result disagree, given that `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
