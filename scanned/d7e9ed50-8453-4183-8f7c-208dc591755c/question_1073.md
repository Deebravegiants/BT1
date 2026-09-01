# Q1073: verify — no destination validation via body_type

## Question
Does `Clients::HttpRequest#verify` collapse two distinct identities into one when an unprivileged attacker submits the `body_type` prop, which becomes the `Content-Type` header verbatim at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent? Show that nothing at this layer relates `path` to the client's base URI, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `body_type` prop, which becomes the `Content-Type` header verbatim
- Exploit idea: nothing at this layer relates `path` to the client's base URI
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
