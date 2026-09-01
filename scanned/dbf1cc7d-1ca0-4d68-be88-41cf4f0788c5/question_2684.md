# Q2684: decode_token — rotation widens acceptance via Bearer prefix games

## Question
If an unprivileged attacker submits an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix to the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`, does `JwtPayload#decode_token` end up acting on a value that was never authenticated, because the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
