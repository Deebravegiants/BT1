# Q614: send_to_logger — no sanitisation via response-derived messages

## Question
Trace `Logger.send_to_logger` from the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger` with deprecation reasons and error messages built from upstream response content in `HttpClient#request`: because no redaction pass exists for tokens, secrets or newlines before writing, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the shop prefix matches the shop of the request being served, not a stale thread-local
