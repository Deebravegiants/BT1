# Q2600: shopify_user_id — rotation widens acceptance via missing claims

## Question
If an unprivileged attacker submits a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths to `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, does `JwtPayload#shopify_user_id` end up acting on a value that was never authenticated, because the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
