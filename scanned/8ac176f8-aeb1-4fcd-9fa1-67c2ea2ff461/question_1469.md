# Q1469: build_check_query — regex injection via path with scheme

## Question
Is there a reachable state in which an unprivileged attacker, controlling a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address at `build_check_query`, which interpolates `@topic` into a GraphQL document, makes `Registrations::Http#build_check_query` return a result the caller treats as authenticated, given that an unescaped interpolation into a `Regexp` changes what the match accepts? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a regex-metacharacter host name does not widen what `callback_address` accepts
