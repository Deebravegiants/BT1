# Q108: validate — encoding-dependent digest via length-varied digest

## Question
If an unprivileged attacker submits a digest of the wrong length, exercising `secure_compare`'s length handling to `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, does `HmacValidator.validate` end up acting on a value that was never authenticated, because `hexdigest` over a differently-encoded string yields a different digest for the same logical content? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: a digest of the wrong length, exercising `secure_compare`'s length handling
- Exploit idea: `hexdigest` over a differently-encoded string yields a different digest for the same logical content
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.old_api_secret_key`, sign under it, and assert `validate` accepts long after rotation
