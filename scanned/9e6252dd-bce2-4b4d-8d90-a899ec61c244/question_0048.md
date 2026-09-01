# Q48: Clients::HttpRequest — verify checks shape, not safety via body_type

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `body_type` prop, which becomes the `Content-Type` header verbatim at the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`, makes `Clients::HttpRequest` return a result the caller treats as authenticated, given that `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `body_type` prop, which becomes the `Content-Type` header verbatim
- Exploit idea: `verify` only validates the method enum and body/body_type pairing; it never inspects `path`, `query` or `extra_headers`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
