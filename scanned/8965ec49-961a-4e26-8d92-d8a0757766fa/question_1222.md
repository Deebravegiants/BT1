# Q1222: deprecated — debug paths carry credentials via log level

## Question
Can the configured `log_level`, which decides whether debug lines carrying request context are emitted, supplied by an unprivileged attacker at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, make `Logger.deprecated` and the code consuming its result disagree, given that debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: the configured `log_level`, which decides whether debug lines carrying request context are emitted
- Exploit idea: debug logging around token flows can include request or error detail derived from bodies that carried `client_secret`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
