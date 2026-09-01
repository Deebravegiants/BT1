# Q2526: decode_token — leeway on both ends via iss suffix

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?` at the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`, makes `JwtPayload#decode_token` return a result the caller treats as authenticated, given that a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
