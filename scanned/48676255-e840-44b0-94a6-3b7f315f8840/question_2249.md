# Q2249: trusted_domains — normalisation happens after the decision via nested host in path

## Question
Does `ShopValidator.trusted_domains` collapse two distinct identities into one when an unprivileged attacker submits a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example` at `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only? Show that the value returned is `uri.host`, not the fully normalised string the caller later interpolates, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a unified-admin URL whose last path segment is itself a hostname, e.g. `https://admin.shopify.com/store/evil.example`
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
