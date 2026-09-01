# Q962: shop — separator collision via dest with embedded separator

## Question
If an unprivileged attacker submits a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator to `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, does `JwtPayload#shop` end up acting on a value that was never authenticated, because the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator
- Exploit idea: the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
