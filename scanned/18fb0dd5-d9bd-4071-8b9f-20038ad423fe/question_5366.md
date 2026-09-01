# Q5366: decode_token — separator collision via iss/dest mismatch

## Question
Can a token whose `iss` and `dest` claims name different shops, which the constructor never compares, supplied by an unprivileged attacker at the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`, make `JwtPayload#decode_token` and the code consuming its result disagree, given that the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a token whose `iss` and `dest` claims name different shops, which the constructor never compares
- Exploit idea: the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
