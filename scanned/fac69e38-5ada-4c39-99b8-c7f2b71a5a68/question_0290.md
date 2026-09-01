# Q290: initialize — claim trusted as identity via leeway window

## Question
If an unprivileged attacker submits a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf` to `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header, does `JwtPayload#initialize` end up acting on a value that was never authenticated, because a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#initialize`
- Entrypoint: `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header
- Attacker controls: a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf`
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
