# Q32: initialize — shop never domain-validated via iss suffix

## Question
Can an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`, supplied by an unprivileged attacker at `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header, make `JwtPayload#initialize` and the code consuming its result disagree, given that the derived `shop` string is used as a request host and a session key without `ShopValidator`? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#initialize`
- Entrypoint: `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header
- Attacker controls: an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
