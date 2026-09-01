# Q331: verify — content-type is caller text via extra_headers

## Question
Does `Clients::HttpRequest#verify` collapse two distinct identities into one when an unprivileged attacker submits the `extra_headers` prop, merged over the client's own headers at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent? Show that `body_type` is written straight into the header with no vocabulary check, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `extra_headers` prop, merged over the client's own headers
- Exploit idea: `body_type` is written straight into the header with no vocabulary check
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
