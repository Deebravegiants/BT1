# Q5179: trusted_domains — trusted list widened per call via trailing-dot host

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ at `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only, makes `ShopValidator.trusted_domains` return a result the caller treats as authenticated, given that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
