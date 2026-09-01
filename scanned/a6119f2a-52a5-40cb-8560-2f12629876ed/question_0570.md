# Q570: deprecated — attacker text into logs via error message content

## Question
If an unprivileged attacker submits the `serialized_error` JSON, which is built from response body and headers to `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, does `Logger.deprecated` end up acting on a value that was never authenticated, because strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: the `serialized_error` JSON, which is built from response body and headers
- Exploit idea: strings taken from a response are logged verbatim, so an upstream-influenced value shapes log content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: stub a response with a deprecation header containing newlines and assert the emitted log line count is unchanged
