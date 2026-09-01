# Q1780: validate_signature — truthiness instead of presence via blank old secret

## Question
Does `HmacValidator.validate_signature` collapse two distinct identities into one when an unprivileged attacker submits an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`? Show that the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs
- Exploit idea: the guard tests truthiness of `hmac`, not that it is a well-formed digest of the right length
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
