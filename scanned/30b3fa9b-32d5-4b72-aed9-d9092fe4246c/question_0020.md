# Q20: online_token? — struct coercion via expires_in absent

## Question
Is there a reachable state in which an unprivileged attacker, controlling an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, makes `Oauth::AccessTokenResponse#online_token?` return a result the caller treats as authenticated, given that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
