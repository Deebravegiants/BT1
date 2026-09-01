# Q181: deprecated — no sanitisation via newline injection

## Question
Is there a reachable state in which an unprivileged attacker, controlling response-controlled strings containing newlines, which forge additional log lines at `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed, makes `Logger.deprecated` return a result the caller treats as authenticated, given that no redaction pass exists for tokens, secrets or newlines before writing? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/logger.rb` -> `Logger.deprecated`
- Entrypoint: `deprecated(message, version)`, which raises `FeatureDeprecatedError` when the version has passed
- Attacker controls: response-controlled strings containing newlines, which forge additional log lines
- Exploit idea: no redaction pass exists for tokens, secrets or newlines before writing
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert no code path logs `access_token`, `refresh_token` or `client_secret`, by asserting on a captured logger
