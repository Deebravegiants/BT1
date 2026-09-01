# Q1093: Clients::HttpRequest — headers merged without an allow-list via path value

## Question
Starting from the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`, can an unprivileged attacker supply the `path` prop, which `verify` never inspects so that any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::HttpRequest`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `path` prop, which `verify` never inspects
- Exploit idea: any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
