# Q1860: validate_signature — secret selected before value is bounded via blank old secret

## Question
Trace `HmacValidator.validate_signature` from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` with an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs: because which secret verifies is decided by the result of the first comparison, an attacker-observable oracle, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an `old_api_secret_key` set to an empty or whitespace string, altering which branch runs
- Exploit idea: which secret verifies is decided by the result of the first comparison, an attacker-observable oracle
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.old_api_secret_key`, sign under it, and assert `validate` accepts long after rotation
