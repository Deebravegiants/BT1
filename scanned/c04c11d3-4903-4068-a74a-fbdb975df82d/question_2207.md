# Q2207: validate_signature — verified value discarded via absent hmac

## Question
Does `HmacValidator.validate_signature` collapse two distinct identities into one when an unprivileged attacker submits an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit at the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`? Show that the object verified is not the object subsequently acted on, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate_signature`
- Entrypoint: the private `validate_signature`, which calls `OpenSSL.secure_compare(computed_signature, received_signature)`
- Attacker controls: an omitted or nil signature, which takes the `return false unless verifiable_query.hmac` short-circuit
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
