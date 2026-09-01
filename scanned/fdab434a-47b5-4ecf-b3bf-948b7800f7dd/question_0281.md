# Q281: verify — content-type is caller text via body_type

## Question
Starting from `HttpRequest#verify`, the only validation applied to an outbound request before it is sent, can an unprivileged attacker supply the `body_type` prop, which becomes the `Content-Type` header verbatim so that `body_type` is written straight into the header with no vocabulary check? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Clients::HttpRequest#verify`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `body_type` prop, which becomes the `Content-Type` header verbatim
- Exploit idea: `body_type` is written straight into the header with no vocabulary check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
