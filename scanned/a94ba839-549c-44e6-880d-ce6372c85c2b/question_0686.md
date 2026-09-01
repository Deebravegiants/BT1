# Q686: shopify_user_id — claim trusted as identity via non-Shopify dest

## Question
Can an unprivileged attacker reach `JwtPayload#shopify_user_id` through `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?` while supplying a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`, so that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
