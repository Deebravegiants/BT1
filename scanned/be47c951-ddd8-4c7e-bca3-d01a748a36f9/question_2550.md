# Q2550: compute_signature — truthiness instead of presence via old-secret window

## Question
Does `HmacValidator.compute_signature` collapse two distinct identities into one when an unprivileged attacker submits a signature valid only under `Context.old_api_secret_key`, which the fallback branch accepts indefinitely at `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`? Show that the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: a signature valid only under `Context.old_api_secret_key`, which the fallback branch accepts indefinitely
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.old_api_secret_key`, sign under it, and assert `validate` accepts long after rotation
