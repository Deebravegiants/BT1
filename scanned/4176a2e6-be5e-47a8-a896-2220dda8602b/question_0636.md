# Q636: deprecated — debug paths carry credentials via shop in the prefix

## Question
Is there a reachable state in which an unprivileged attacker, controlling the active session's shop, embedded in every line, which reveals which tenant a worker is serving at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, makes `Logger.deprecated` return a result the caller treats as authenticated, given that debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: the active session's shop, embedded in every line, which reveals which tenant a worker is serving
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
