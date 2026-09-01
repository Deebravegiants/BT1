# Q3464: admin_session_token? — rotation widens acceptance via missing claims

## Question
Is there a reachable state in which an unprivileged attacker, controlling a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths at `admin_session_token?`, a bare `@iss.end_with?("/admin")` check, makes `JwtPayload#admin_session_token?` return a result the caller treats as authenticated, given that the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
