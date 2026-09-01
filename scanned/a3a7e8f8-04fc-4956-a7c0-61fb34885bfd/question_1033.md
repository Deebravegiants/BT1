# Q1033: verify — content-type is caller text via method/body combinations

## Question
Can combinations of `http_method` and `body` that sit at the edges of the three `verify` checks, supplied by an unprivileged attacker at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent, make `Clients::HttpRequest#verify` and the code consuming its result disagree, given that `body_type` is written straight into the header with no vocabulary check? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: combinations of `http_method` and `body` that sit at the edges of the three `verify` checks
- Exploit idea: `body_type` is written straight into the header with no vocabulary check
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
