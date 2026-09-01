# Q786: Clients::HttpRequest — content-type is caller text via query hash

## Question
Does `Clients::HttpRequest` collapse two distinct identities into one when an unprivileged attacker submits the `query` prop, forwarded to HTTParty unvalidated at the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`? Show that `body_type` is written straight into the header with no vocabulary check, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: `body_type` is written straight into the header with no vocabulary check
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
