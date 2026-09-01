# Q136: shopify_user_id — shop never domain-validated via sid claim

## Question
If an unprivileged attacker submits the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity to `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, does `JwtPayload#shopify_user_id` end up acting on a value that was never authenticated, because the derived `shop` string is used as a request host and a session key without `ShopValidator`? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
