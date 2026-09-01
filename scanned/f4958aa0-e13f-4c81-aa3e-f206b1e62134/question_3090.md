# Q3090: decode_token — shop never domain-validated via iss suffix

## Question
If an unprivileged attacker submits an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?` to the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`, does `JwtPayload#decode_token` end up acting on a value that was never authenticated, because the derived `shop` string is used as a request host and a session key without `ShopValidator`? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
