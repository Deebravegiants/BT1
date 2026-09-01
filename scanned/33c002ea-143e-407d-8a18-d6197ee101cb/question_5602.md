# Q5602: unified_admin? — trusted list widened per call via IDN / Unicode label

## Question
Does `ShopValidator.unified_admin?` collapse two distinct identities into one when an unprivileged attacker submits a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip` at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`? Show that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
