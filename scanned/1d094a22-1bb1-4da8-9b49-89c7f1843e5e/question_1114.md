# Q1114: send_to_logger — tenant identity in every line via log level

## Question
Starting from the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`, can an unprivileged attacker supply the configured `log_level`, which decides whether debug lines carrying request context are emitted so that the shop prefix is derived from thread-local state that may be stale? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Logger.send_to_logger`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
