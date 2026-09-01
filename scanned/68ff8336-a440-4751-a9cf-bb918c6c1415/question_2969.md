# Q2969: decode_token — leeway on both ends via own-shop id token

## Question
Starting from the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`, can an unprivileged attacker supply a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app so that a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `JwtPayload#decode_token`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
