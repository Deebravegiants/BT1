# Q4468: sanitize_shop_domain — parse/resolve divergence via IDN / Unicode label

## Question
Does `ShopValidator.sanitize_shop_domain` collapse two distinct identities into one when an unprivileged attacker submits a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip` at a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`? Show that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string using non-ASCII or Unicode-normalising labels (fullwidth dot, Cyrillic homoglyph, soft hyphen) that survive `downcase.strip`
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
