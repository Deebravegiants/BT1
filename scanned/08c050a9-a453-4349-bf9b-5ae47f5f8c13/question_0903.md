# Q903: append_first_party_development_headers — response content into logs via path traversal segments

## Question
Can an unprivileged attacker reach `Clients::HttpClient#append_first_party_development_headers` through `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev` while supplying `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path, so that response-controlled strings reach `Context.logger` and the exception message alongside request context, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: `../` or `%2e%2e%2f` segments in `path` that climb out of the versioned base path
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
