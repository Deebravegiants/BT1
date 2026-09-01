# Q615: uri_from_shop_domain — trusted list widened per call via userinfo bypass

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped at the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`, makes `ShopValidator.uri_from_shop_domain` return a result the caller treats as authenticated, given that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
