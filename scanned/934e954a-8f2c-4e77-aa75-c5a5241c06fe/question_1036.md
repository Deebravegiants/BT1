# Q1036: deprecated — attacker text into logs via response-derived messages

## Question
Can an unprivileged attacker reach `Logger.deprecated` through `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed while supplying deprecation reasons and error messages built from upstream response content in `HttpClient#request`, so that strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: deprecation reasons and error messages built from upstream response content in `HttpClient#request`
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
