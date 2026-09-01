# Q1952: validate_signature — fallback never expires via non-ASCII signable string

## Question
Is there a reachable state in which an unprivileged attacker, controlling a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, makes `HmacValidator.validate_signature` return a result the caller treats as authenticated, given that the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification
- Exploit idea: the `old_api_secret_key` branch has no cutoff, so a rotated secret remains a valid signing key forever
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
