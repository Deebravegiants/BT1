# Q4213: admin_session_token? — leeway on both ends via non-Shopify dest

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator` at `admin_session_token?`, a bare `@iss.end_with?("/admin")` check, makes `JwtPayload#admin_session_token?` return a result the caller treats as authenticated, given that a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a `dest` naming a host outside `TRUSTED_SHOPIFY_DOMAINS`, since `JwtPayload` never calls `ShopValidator`
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
