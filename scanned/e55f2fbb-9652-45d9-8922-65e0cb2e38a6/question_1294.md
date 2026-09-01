# Q1294: deprecated — no sanitisation via response-derived messages

## Question
Is there a reachable state in which an unprivileged attacker, controlling deprecation reasons and error messages built from upstream response content in `HttpClient#request` at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, makes `Logger.deprecated` return a result the caller treats as authenticated, given that no redaction pass exists for tokens, secrets or newlines before writing? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
