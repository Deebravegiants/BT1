# Q4864: sanitize_shop_domain — parse/resolve divergence via dotless name

## Question
Is there a reachable state in which an unprivileged attacker, controlling a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input at a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, makes `ShopValidator.sanitize_shop_domain` return a result the caller treats as authenticated, given that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
