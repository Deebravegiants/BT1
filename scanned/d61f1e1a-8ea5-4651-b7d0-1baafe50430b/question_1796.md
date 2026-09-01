# Q1796: validate_signature — verified value discarded via empty-string hmac

## Question
Can an empty signature string, which is truthy in Ruby and reaches `secure_compare`, supplied by an unprivileged attacker at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, make `HmacValidator.validate_signature` and the code consuming its result disagree, given that the object verified is not the object subsequently acted on? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an empty signature string, which is truthy in Ruby and reaches `secure_compare`
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
