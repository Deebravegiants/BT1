# Q1016: context — debug paths carry credentials via log level

## Question
Starting from `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line, can an unprivileged attacker supply the configured `log_level`, which decides whether debug lines carrying request context are emitted so that debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Logger.context`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.context`
- Entrypoint: `context`, which embeds `ShopifyAPI::Context.active_session&.shop` in every log line
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
