# Q4979: sanitize_shop_domain — validated value discarded via backslash separator

## Question
Does `ShopValidator.sanitize_shop_domain` collapse two distinct identities into one when an unprivileged attacker submits a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about at a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`? Show that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
