# Q1276: send_to_logger — debug paths carry credentials via newline injection

## Question
Does `Logger.send_to_logger` collapse two distinct identities into one when an unprivileged attacker submits response-controlled strings containing newlines, which forge additional log lines at the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`? Show that debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
