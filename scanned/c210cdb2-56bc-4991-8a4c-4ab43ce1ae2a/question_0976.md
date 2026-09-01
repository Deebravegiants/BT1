# Q976: context — tenant identity in every line via response-derived messages

## Question
If an unprivileged attacker submits deprecation reasons and error messages built from upstream response content in `HttpClient#request` to `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, does `Logger.context` end up acting on a value that was never authenticated, because the shop prefix is derived from thread-local state that may be stale? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
