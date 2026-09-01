# Q1056: deprecated — attacker text into logs via newline injection

## Question
Is there a reachable state in which an unprivileged attacker, controlling response-controlled strings containing newlines, which forge additional log lines at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, makes `Logger.deprecated` return a result the caller treats as authenticated, given that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
