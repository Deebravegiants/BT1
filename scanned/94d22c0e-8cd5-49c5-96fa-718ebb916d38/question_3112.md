# Q3112: shopify_user_id — no iss/dest binding via sid claim

## Question
Can the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity, supplied by an unprivileged attacker at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, make `JwtPayload#shopify_user_id` and the code consuming its result disagree, given that the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity
- Exploit idea: the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
