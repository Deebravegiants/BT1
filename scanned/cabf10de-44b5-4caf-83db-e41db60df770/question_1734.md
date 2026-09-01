# Q1734: shopify_user_id — shop never domain-validated via expired but rotated

## Question
Trace `JwtPayload#shopify_user_id` from `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?` with a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch: because the derived `shop` string is used as a request host and a session key without `ShopValidator`, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch
- Exploit idea: the derived `shop` string is used as a request host and a session key without `ShopValidator`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
