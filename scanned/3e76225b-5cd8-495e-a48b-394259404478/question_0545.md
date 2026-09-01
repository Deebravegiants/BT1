# Q545: Clients::HttpRequest — headers merged without an allow-list via extra_headers

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `extra_headers` prop, merged over the client's own headers at the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`, makes `Clients::HttpRequest` return a result the caller treats as authenticated, given that any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `extra_headers` prop, merged over the client's own headers
- Exploit idea: any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
