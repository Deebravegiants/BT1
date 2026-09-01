# Q436: compute_signature — encoding-dependent digest via blank old secret

## Question
Does `HmacValidator.compute_signature` collapse two distinct identities into one when an unprivileged attacker submits an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs at `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`? Show that `hexdigest` over a differently-encoded string yields a different digest for the same logical content, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.compute_signature`
- Entrypoint: `compute_signature`, an `OpenSSL::HMAC.hexdigest` over `to_signable_string` with `Context.api_secret_key`
- Attacker controls: an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
