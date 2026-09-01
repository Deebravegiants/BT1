# Q2729: unified_admin? — normalisation happens after the decision via suffix-confusion host

## Question
Is there a reachable state in which an unprivileged attacker, controlling a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com` at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, makes `ShopValidator.unified_admin?` return a result the caller treats as authenticated, given that the value returned is `uri.host`, not the fully normalised string the caller later interpolates? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a host whose registrable domain matches a trusted entry only under `Addressable`'s public-suffix view, e.g. `myshopify.com.evil.example` or `evil-myshopify.com`
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven minitest asserting `sanitize_shop_domain` returns `nil` for the candidate string, then assert the same string through `URI`/HTTParty resolves elsewhere
