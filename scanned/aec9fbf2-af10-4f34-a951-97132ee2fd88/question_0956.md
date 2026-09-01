# Q956: send_to_logger — attacker text into logs via log level

## Question
Can the configured `log_level`, which decides whether debug lines carrying request context are emitted, supplied by an unprivileged attacker at the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`, make `Logger.send_to_logger` and the code consuming its result disagree, given that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
