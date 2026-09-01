# Q188: admin_session_token? — unanchored substitution via leeway window

## Question
Is there a reachable state in which an unprivileged attacker, controlling a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf` at `admin_session_token?`, a bare `@iss.end_with?("/admin")` check, makes `JwtPayload#admin_session_token?` return a result the caller treats as authenticated, given that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf`
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
