# Q1280: validate_signature — authenticity is not authorisation via shared-secret multi-tenant

## Question
Is there a reachable state in which an unprivileged attacker, controlling a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`, makes `HmacValidator.validate_signature` return a result the caller treats as authenticated, given that a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
