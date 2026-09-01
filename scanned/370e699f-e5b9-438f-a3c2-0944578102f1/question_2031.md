# Q2031: request — attacker-steered retry loop via extra_headers

## Question
Starting from `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, can an unprivileged attacker supply `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type` so that response headers decide how long and how often the authenticated request is repeated? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::HttpClient#request`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
