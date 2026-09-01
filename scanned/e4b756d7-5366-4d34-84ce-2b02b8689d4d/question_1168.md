# Q1168: context — attacker text into logs via response-derived messages

## Question
Is there a reachable state in which an unprivileged attacker, controlling deprecation reasons and error messages built from upstream response content in `HttpClient#request` at `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, makes `Logger.context` return a result the caller treats as authenticated, given that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
