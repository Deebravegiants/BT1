# Q1186: send_to_logger — tenant identity in every line via newline injection

## Question
If an unprivileged attacker submits response-controlled strings containing newlines, which forge additional log lines to the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`, does `Logger.send_to_logger` end up acting on a value that was never authenticated, because the shop prefix is derived from thread-local state that may be stale? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
