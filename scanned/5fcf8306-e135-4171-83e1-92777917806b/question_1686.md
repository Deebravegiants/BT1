# Q1686: shop — shop never domain-validated via non-Shopify dest

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator` at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, makes `JwtPayload#shop` return a result the caller treats as authenticated, given that the derived `shop` string is used as a request host and a session key without `ShopValidator`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
