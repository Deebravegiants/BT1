# Q3219: unified_admin? — shop name reconstructed, not validated via IDN / Unicode label

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip` at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, makes `ShopValidator.unified_admin?` return a result the caller treats as authenticated, given that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
