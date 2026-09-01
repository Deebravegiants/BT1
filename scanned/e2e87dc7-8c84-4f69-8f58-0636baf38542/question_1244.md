# Q1244: validate_signature — encoding-dependent digest via absent hmac

## Question
Trace `HmacValidator.validate_signature` from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)` with an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit: because `hexdigest` over a differently-encoded string yields a different digest for the same logical content, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
