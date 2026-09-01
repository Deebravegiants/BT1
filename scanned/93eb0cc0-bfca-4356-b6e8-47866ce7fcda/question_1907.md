# Q1907: validate — verified value discarded via shared-secret multi-tenant

## Question
If an unprivileged attacker submits a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app to `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook, does `HmacValidator.validate` end up acting on a value that was never authenticated, because the object verified is not the object subsequently acted on? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/hmac_validator.rb` -> `HmacValidator.validate`
- Entrypoint: `ShopifyAPI::Utils::HmacValidator.validate`, the single arbiter of authenticity for both the OAuth callback and every inbound webhook
- Attacker controls: a validly signed artefact from the attacker's own shop, since one `api_secret_key` covers every shop that installed the app
- Exploit idea: the object verified is not the object subsequently acted on
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: sign a body as UTF-8, re-present it as ASCII-8BIT, and assert the verification verdict is unchanged
