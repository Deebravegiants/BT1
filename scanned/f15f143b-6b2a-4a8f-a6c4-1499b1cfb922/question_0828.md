# Q828: verify — headers merged without an allow-list via query hash

## Question
Does `Clients::HttpRequest#verify` collapse two distinct identities into one when an unprivileged attacker submits the `query` prop, forwarded to HTTParty unvalidated at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent? Show that any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
