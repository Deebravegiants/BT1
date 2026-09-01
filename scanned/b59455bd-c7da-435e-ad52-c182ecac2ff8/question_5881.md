# Q5881: unified_admin? — validator returns a non-Shopify host via embedded port

## Question
Starting from the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, can an unprivileged attacker supply a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example` so that `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `ShopValidator.unified_admin?`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`
- Exploit idea: `sanitize_shop_domain` returns a string that is not a Shopify shop, and that string becomes `@base_uri` in `Clients::HttpClient#initialize`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
