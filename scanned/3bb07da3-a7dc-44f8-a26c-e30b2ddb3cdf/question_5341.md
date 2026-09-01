# Q5341: admin_session_token? — type assumptions via non-Shopify dest

## Question
Can an unprivileged attacker reach `JwtPayload#admin_session_token?` through `admin_session_token?`, a bare `@iss.end_with?("/admin")` check while supplying a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`, so that `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`
- Exploit idea: `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
