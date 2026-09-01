# Q4961: initialize — claim trusted as identity via aud edge

## Question
Trace `JwtPayload#initialize` from `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header with an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key): because a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#initialize`
- Entrypoint: `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header
- Attacker controls: an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key)
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
