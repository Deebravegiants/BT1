# Q848: online_token? — identity shape from the response via expires_in absent

## Question
Starting from `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, can an unprivileged attacker supply an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false so that whether the session is online or offline - and therefore which storage key it occupies - is decided by response content? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::AccessTokenResponse#online_token?`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: whether the session is online or offline - and therefore which storage key it occupies - is decided by response content
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
