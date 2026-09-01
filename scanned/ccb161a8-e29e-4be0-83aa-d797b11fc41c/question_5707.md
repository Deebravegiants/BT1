# Q5707: myshopify_domain_from_unified_admin — validated value discarded via whitespace and control bytes

## Question
Does `ShopValidator.myshopify_domain_from_unified_admin` collapse two distinct identities into one when an unprivileged attacker submits a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does at `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment? Show that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string padded with control bytes, newlines or tabs that `strip` does not remove but a header serialiser does
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: drive `ClientCredentials.client_credentials(shop: candidate)` under WebMock and assert the request body containing `client_secret` was never sent off-domain
