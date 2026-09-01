# Q5518: uri_from_shop_domain — validated value discarded via embedded port

## Question
Does `ShopValidator.uri_from_shop_domain` collapse two distinct identities into one when an unprivileged attacker submits a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example` at the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`? Show that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
