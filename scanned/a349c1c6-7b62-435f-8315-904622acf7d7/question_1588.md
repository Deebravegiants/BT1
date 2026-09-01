# Q1588: validate — authenticity is not authorisation via non-ASCII signable string

## Question
Is there a reachable state in which an unprivileged attacker, controlling a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification at `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, makes `HmacValidator.validate` return a result the caller treats as authenticated, given that a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: a signable string whose encoding (`ASCII-8BIT` vs `UTF-8`) differs between signing and verification
- Exploit idea: a valid signature proves Shopify signed something for some shop, not that it was for this shop, this browser or this topic
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `validate` returns false for an empty-string hmac and for a wrong-length digest
