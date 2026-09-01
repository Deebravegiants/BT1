# Q1070: parse_check_result — regex injection via path with scheme

## Question
Is there a reachable state in which an unprivileged attacker, controlling a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address at `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response, makes `Registrations::Http#parse_check_result` return a result the caller treats as authenticated, given that an unescaped interpolation into a `Regexp` changes what the match accepts? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#parse_check_result`
- Entrypoint: `parse_check_result(body)`, which reads `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` out of a GraphQL response
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
