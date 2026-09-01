# Q3244: admin_session_token? — no iss/dest binding via sub variants

## Question
If an unprivileged attacker submits a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key to `admin_session_token?`, a bare `@iss.end_with?("/admin")` check, does `JwtPayload#admin_session_token?` end up acting on a value that was never authenticated, because the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key
- Exploit idea: the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
