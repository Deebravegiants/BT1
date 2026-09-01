# Q3863: serialized_error — token attached before destination is settled via response-driven retry

## Question
Is there a reachable state in which an unprivileged attacker, controlling a 429 or 500 response with a chosen `retry-after` header, steering the retry loop at `serialized_error`, which builds an error message from response body and headers, makes `Clients::HttpClient#serialized_error` return a result the caller treats as authenticated, given that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a 429 or 500 response with a chosen `retry-after` header, steering the retry loop
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
