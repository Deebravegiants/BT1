# Q4726: admin_session_token? — separator collision via aud edge

## Question
Starting from `admin_session_token?`, a bare `@iss.end_with?("/admin")` check, can an unprivileged attacker supply an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key) so that the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `JwtPayload#admin_session_token?`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key)
- Exploit idea: the derived `shop`/`sub` values contain the `_` that `jwt_session_id` uses as its delimiter
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
