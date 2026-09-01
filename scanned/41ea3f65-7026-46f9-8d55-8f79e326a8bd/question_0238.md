# Q238: compute_signature — truthiness instead of presence via non-ASCII signable string

## Question
Can an unprivileged attacker reach `HmacValidator.compute_signature` through `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key` while supplying a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification, so that the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
