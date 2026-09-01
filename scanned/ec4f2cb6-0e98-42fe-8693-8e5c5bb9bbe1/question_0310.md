# Q310: uri_from_shop_domain — nil-safe guard skipped via backslash separator

## Question
Does `ShopValidator.uri_from_shop_domain` collapse two distinct identities into one when an unprivileged attacker submits a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about at the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`? Show that the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.uri_from_shop_domain`
- Entrypoint: the private `uri_from_shop_domain` normalisation step that downcases, strips, rejects `@` and prepends `https://` before `Addressable::URI.parse`
- Attacker controls: a shop string using a backslash instead of a slash (`https:\\evil.example\admin`), which `Addressable` and HTTParty disagree about
- Exploit idea: the `next if uri_domain.nil?` and `return nil if no_shop_name_in_subdomain` guards are evaluated per trusted domain, so ordering decides the verdict
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
