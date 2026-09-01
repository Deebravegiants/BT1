# Q1102: shopify_user_id — type assumptions via sub variants

## Question
If an unprivileged attacker submits a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key to `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, does `JwtPayload#shopify_user_id` end up acting on a value that was never authenticated, because `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key
- Exploit idea: `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
