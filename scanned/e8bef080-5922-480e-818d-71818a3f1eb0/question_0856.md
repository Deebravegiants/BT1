# Q856: validate_signature — authenticity is not authorisation via non-ASCII signable string

## Question
Does `HmacValidator.validate_signature` collapse two distinct identities into one when an unprivileged attacker submits a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`? Show that a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
