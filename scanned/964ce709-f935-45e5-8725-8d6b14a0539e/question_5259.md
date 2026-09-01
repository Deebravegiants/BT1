# Q5259: myshopify_domain_from_unified_admin — trusted list widened per call via suffix-confusion host

## Question
Does `ShopValidator.myshopify_domain_from_unified_admin` collapse two distinct identities into one when an unprivileged attacker submits a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com` at `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment? Show that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com`
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
