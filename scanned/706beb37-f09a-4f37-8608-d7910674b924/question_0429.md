# Q429: verify — verify checks shape, not safety via tries value

## Question
Does `Clients::HttpRequest#verify` collapse two distinct identities into one when an unprivileged attacker submits the `tries` prop, controlling how many times an authenticated request is repeated at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent? Show that `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `tries` prop, controlling how many times an authenticated request is repeated
- Exploit idea: `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
