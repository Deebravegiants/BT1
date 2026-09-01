# Q100: Clients::HttpRequest — no destination validation via query hash

## Question
Does `Clients::HttpRequest` collapse two distinct identities into one when an unprivileged attacker submits the `query` prop, forwarded to HTTParty unvalidated at the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`? Show that nothing at this layer relates `path` to the client's base URI, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: nothing at this layer relates `path` to the client's base URI
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
