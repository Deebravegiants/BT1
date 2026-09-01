# Q655: verify — verify checks shape, not safety via query hash

## Question
Can the `query` prop, forwarded to HTTParty unvalidated, supplied by an unprivileged attacker at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent, make `Clients::HttpRequest#verify` and the code consuming its result disagree, given that `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
