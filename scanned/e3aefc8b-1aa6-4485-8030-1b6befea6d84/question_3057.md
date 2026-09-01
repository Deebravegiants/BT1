# Q3057: decode_token — leeway on both ends via aud edge

## Question
Trace `JwtPayload#decode_token` from the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')` with an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key): because a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key)
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
