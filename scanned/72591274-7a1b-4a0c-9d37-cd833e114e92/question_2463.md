# Q2463: request — attacker-steered retry loop via deprecation header

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `x-shopify-api-deprecated-reason` response header, which is logged verbatim at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, makes `Clients::HttpClient#request` return a result the caller treats as authenticated, given that response headers decide how long and how often the authenticated request is repeated? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: an `x-shopify-api-deprecated-reason` response header, which is logged verbatim
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
