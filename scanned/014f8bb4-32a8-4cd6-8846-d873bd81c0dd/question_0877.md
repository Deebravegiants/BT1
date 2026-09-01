# Q877: validate — secret selected before value is bounded via non-ASCII signable string

## Question
Does `HmacValidator.validate` collapse two distinct identities into one when an unprivileged attacker submits a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification at `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook? Show that which secret verifies is decided by the result of the first comparison, an attacker-observable oracle, that BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification
- Exploit idea: which secret verifies is decided by the result of the first comparison, an attacker-observable oracle
- Invariant to test: BYTE IDENTITY: the bytes passed to `compute_signature` == the bytes later parsed and acted on
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
