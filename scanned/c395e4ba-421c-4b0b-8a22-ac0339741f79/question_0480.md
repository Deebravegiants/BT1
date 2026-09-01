# Q480: deprecated — tenant identity in every line via error message content

## Question
Can the `serialized_error` JSON, which is built from response body and headers, supplied by an unprivileged attacker at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, make `Logger.deprecated` and the code consuming its result disagree, given that the shop prefix is derived from thread-local state that may be stale? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: the shop prefix is derived from thread-local state that may be stale
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
