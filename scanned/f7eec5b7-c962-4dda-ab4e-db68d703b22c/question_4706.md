# Q4706: admin_session_token? — separator collision via leeway window

## Question
Does `JwtPayload#admin_session_token?` collapse two distinct identities into one when an unprivileged attacker submits a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf` at `admin_session_token?`, a bare `@iss.end_with?("/admin")` check? Show that the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf`
- Exploit idea: the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
