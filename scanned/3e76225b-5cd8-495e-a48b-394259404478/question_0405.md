# Q405: verify — content-type is caller text via query hash

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `query` prop, forwarded to HTTParty unvalidated at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent, makes `Clients::HttpRequest#verify` return a result the caller treats as authenticated, given that `body_type` is written straight into the header with no vocabulary check? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: `body_type` is written straight into the header with no vocabulary check
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: pass `extra_headers` overriding `X-Shopify-Access-Token` and assert the recorded request used the session's token
