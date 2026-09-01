# Q702: send_to_logger — no sanitisation via newline injection

## Question
Does `Logger.send_to_logger` collapse two distinct identities into one when an unprivileged attacker submits response-controlled strings containing newlines, which forge additional log lines at the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`? Show that no redaction pass exists for tokens, secrets or newlines before writing, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
