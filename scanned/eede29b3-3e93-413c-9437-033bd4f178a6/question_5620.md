# Q5620: sanitize_shop_domain — validated value discarded via userinfo bypass

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped at a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`, makes `ShopValidator.sanitize_shop_domain` return a result the caller treats as authenticated, given that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.sanitize_shop_domain`
- Entrypoint: a host-app route that forwards a user-supplied `shop` query parameter into `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain`
- Attacker controls: a shop string that expresses userinfo without a literal `@` (encoded `%40`) so the `name.include?("@")` guard is skipped
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
