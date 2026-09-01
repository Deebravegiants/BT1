# Q1345: trusted_domains — validated value discarded via userinfo bypass

## Question
Starting from `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only, can an unprivileged attacker supply a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped so that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `ShopValidator.trusted_domains`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
