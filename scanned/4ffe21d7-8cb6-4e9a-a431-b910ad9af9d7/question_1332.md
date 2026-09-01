# Q1332: validate_signature — secret selected before value is bounded via case-varied digest

## Question
Does `HmacValidator.validate_signature` collapse two distinct identities into one when an unprivileged attacker submits an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`? Show that which secret verifies is decided by the result of the first comparison, an attacker-observable oracle, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an uppercase or mixed-case hex digest compared byte-wise against the lowercase `hexdigest` output
- Exploit idea: which secret verifies is decided by the result of the first comparison, an attacker-observable oracle
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.old_api_secret_key`, sign under it, and assert `validate` accepts long after rotation
