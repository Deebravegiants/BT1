# Q4696: shopify_user_id — unanchored substitution via own-shop id token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, makes `JwtPayload#shopify_user_id` return a result the caller treats as authenticated, given that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
