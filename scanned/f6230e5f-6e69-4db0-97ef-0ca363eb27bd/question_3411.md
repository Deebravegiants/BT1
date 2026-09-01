# Q3411: request_url — response content into logs via error body content

## Question
Does `Clients::HttpClient#request_url` collapse two distinct identities into one when an unprivileged attacker submits a response body whose `errors`/`error_description` fields are echoed into the raised exception message at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation? Show that response-controlled strings reach `Context.logger` and the exception message alongside request context, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
