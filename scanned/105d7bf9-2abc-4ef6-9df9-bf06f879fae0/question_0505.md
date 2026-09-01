# Q505: myshopify_domain_from_unified_admin — trusted list widened per call via scheme injection

## Question
Starting from `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, can an unprivileged attacker supply a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://` so that `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `ShopValidator.myshopify_domain_from_unified_admin`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a shop string that already carries a scheme (`http://`, `//`, `javascript:`, `file:`) so the `uri.scheme.nil?` branch never prepends `https://`
- Exploit idea: `trusted_domains` mutates a dup of the constant with a caller-supplied value, so the trust set is request-scoped
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
