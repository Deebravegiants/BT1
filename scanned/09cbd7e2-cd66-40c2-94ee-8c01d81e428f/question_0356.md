# Q356: verify — headers merged without an allow-list via method/body combinations

## Question
Is there a reachable state in which an unprivileged attacker, controlling combinations of `http_method` and `body` that sit at the edges of the three `verify` checks at `HttpRequest#verify`, the only validation applied to an outbound request before it is sent, makes `Clients::HttpRequest#verify` return a result the caller treats as authenticated, given that any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/http_request.rb` -> `Clients::HttpRequest#verify`
- Entrypoint: `HttpRequest#verify`, the only validation applied to an outbound request before it is sent
- Attacker controls: combinations of `http_method` and `body` that sit at the edges of the three `verify` checks
- Exploit idea: any key in `extra_headers` can override `X-Shopify-Access-Token`, `Host` or `Accept`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `verify` rejects a `path` that changes the authority of the final URL
