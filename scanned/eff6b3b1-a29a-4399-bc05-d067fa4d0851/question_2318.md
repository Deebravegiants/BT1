# Q2318: initialize — claim trusted as identity via non-Shopify dest

## Question
Starting from `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header, can an unprivileged attacker supply a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator` so that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `JwtPayload#initialize`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#initialize`
- Entrypoint: `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header
- Attacker controls: a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
