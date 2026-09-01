# Q484: validate_signature — verified value discarded via old-secret window

## Question
Starting from the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, can an unprivileged attacker supply a signature valid only under `Context.old_api_secret_key`, which the fallback branch accepts indefinitely so that the object verified is not the object subsequently acted on? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `HmacValidator.validate_signature`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a signature valid only under `Context.old_api_secret_key`, which the fallback branch accepts indefinitely
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
