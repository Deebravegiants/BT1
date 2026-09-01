# Q3103: serialized_error — response content into logs via error body content

## Question
Does `Clients::HttpClient#serialized_error` collapse two distinct identities into one when an unprivileged attacker submits a response body whose `errors`/`error_description` fields are echoed into the raised exception message at `serialized_error`, which builds an error message from response body and headers? Show that response-controlled strings reach `Context.logger` and the exception message alongside request context, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
