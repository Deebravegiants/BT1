# Q5554: myshopify_domain_from_unified_admin — parse/resolve divergence via IDN / Unicode label

## Question
If an unprivileged attacker submits a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip` to `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, does `ShopValidator.myshopify_domain_from_unified_admin` end up acting on a value that was never authenticated, because what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
