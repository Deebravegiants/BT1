# Q1013: verify — verify checks shape, not safety via body_type

## Question
Trace `Clients::HttpRequest#verify` from `HttpRequest#verify`, the only validation applied to an outbound request before it is sent with the `body_type` prop, which becomes the `Content-Type` header verbatim: because `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `body_type` prop, which becomes the `Content-Type` header verbatim
- Exploit idea: `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
