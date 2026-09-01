# Q1123: serialized_error — response content into logs via scheme in path

## Question
If an unprivileged attacker submits a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL to `serialized_error`, which builds an error message from response body and headers, does `Clients::HttpClient#serialized_error` end up acting on a value that was never authenticated, because response-controlled strings reach `Context.logger` and the exception message alongside request context? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
