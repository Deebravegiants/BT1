# Q1638: decode_token — separator collision via missing claims

## Question
Can an unprivileged attacker reach `JwtPayload#decode_token` through the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')` while supplying a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths, so that the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`?

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths
- Exploit idea: the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
