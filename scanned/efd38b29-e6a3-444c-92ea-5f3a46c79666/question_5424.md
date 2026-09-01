# Q5424: unified_admin? — parse/resolve divergence via caller-supplied myshopify_domain

## Question
Is there a reachable state in which an unprivileged attacker, controlling a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`, makes `ShopValidator.unified_admin?` return a result the caller treats as authenticated, given that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
