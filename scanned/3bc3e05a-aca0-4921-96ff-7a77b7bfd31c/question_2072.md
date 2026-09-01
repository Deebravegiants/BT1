# Q2072: compute_signature — encoding-dependent digest via absent hmac

## Question
Can an unprivileged attacker reach `HmacValidator.compute_signature` through `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key` while supplying an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit, so that `hexdigest` over a differently-encoded string yields a different digest for the same logical content, breaking the requirement that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
