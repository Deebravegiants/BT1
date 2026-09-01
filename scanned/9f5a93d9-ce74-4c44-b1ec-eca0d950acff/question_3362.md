# Q3362: trusted_domains — parse/resolve divergence via caller-supplied myshopify_domain

## Question
Does `ShopValidator.trusted_domains` collapse two distinct identities into one when an unprivileged attacker submits a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call at `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only? Show that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
