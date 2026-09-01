# Q5958: trusted_domains — path segment trusted as identity via trailing-dot host

## Question
Starting from `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only, can an unprivileged attacker supply a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ so that the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `ShopValidator.trusted_domains`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a shop string with a fully-qualified trailing dot such as `victim.myshopify.com.` so that the parsed `domain` and the host an HTTP client actually resolves differ
- Exploit idea: the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
