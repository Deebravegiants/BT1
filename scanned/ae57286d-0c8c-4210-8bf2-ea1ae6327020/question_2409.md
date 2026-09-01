# Q2409: shopify_user_id — no iss/dest binding via leeway window

## Question
Starting from `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, can an unprivileged attacker supply a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf` so that the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `JwtPayload#shopify_user_id`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a token replayed inside the 10-second `JWT_LEEWAY` on both `exp` and `nbf`
- Exploit idea: the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
