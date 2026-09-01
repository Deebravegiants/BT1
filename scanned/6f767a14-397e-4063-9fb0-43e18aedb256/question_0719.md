# Q719: online_token? — identity shape from the response via scope mismatch

## Question
Trace `Oauth::AccessTokenResponse#online_token?` from `online_token?`, which decides online vs offline purely by `!associated_user.nil?` with a `scope` string that does not match what the app requested at `begin_auth`: because whether the session is online or offline - and therefore which storage key it occupies - is decided by response content, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: a `scope` string that does not match what the app requested at `begin_auth`
- Exploit idea: whether the session is online or offline - and therefore which storage key it occupies - is decided by response content
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
