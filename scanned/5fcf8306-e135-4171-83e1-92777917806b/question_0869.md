# Q869: from_hash — identity shape from the response via scope mismatch

## Question
Starting from `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, can an unprivileged attacker supply a `scope` string that does not match what the app requested at `begin_auth` so that whether the session is online or offline - and therefore which storage key it occupies - is decided by response content? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::AccessTokenResponse.from_hash`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: a `scope` string that does not match what the app requested at `begin_auth`
- Exploit idea: whether the session is online or offline - and therefore which storage key it occupies - is decided by response content
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
