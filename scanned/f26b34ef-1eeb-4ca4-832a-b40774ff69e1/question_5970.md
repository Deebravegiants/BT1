# Q5970: unified_admin? — shop name reconstructed, not validated via embedded port

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example` at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, makes `ShopValidator.unified_admin?` return a result the caller treats as authenticated, given that the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`
- Exploit idea: the returned `"#{shop}.myshopify.com"` is manufactured by string concatenation and never re-validated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `sanitize!` raises `Errors::InvalidShopError` for the input; if it returns, print the value and diff it against the host in the recorded WebMock request
