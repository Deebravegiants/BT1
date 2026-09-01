# Q230: Clients::HttpRequest — headers merged without an allow-list via query hash

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `query` prop, forwarded to HTTParty unvalidated at the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`, makes `Clients::HttpRequest` return a result the caller treats as authenticated, given that any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest`
- Entrypoint: the `HttpRequest` struct itself, carrying `http_method`, `path`, `body`, `body_type`, `query`, `extra_headers` and `tries`
- Attacker controls: the `query` prop, forwarded to HTTParty unvalidated
- Exploit idea: any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
