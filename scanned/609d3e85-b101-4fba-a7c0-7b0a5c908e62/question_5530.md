# Q5530: uri_from_shop_domain — trusted list widened per call via embedded port

## Question
Can an unprivileged attacker reach `ShopValidator.uri_from_shop_domain` through the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse` while supplying a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`, so that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
