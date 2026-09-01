# Q1258: send_to_logger — attacker text into logs via shop in the prefix

## Question
Trace `Logger.send_to_logger` from the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger` with the active session's shop, embedded in every line, which reveals which tenant a worker is serving: because strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.send_to_logger`
- Entrypoint: the private `send_to_logger`, which prefixes every message with `context(log_level)` and forwards to `Context.logger`
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
