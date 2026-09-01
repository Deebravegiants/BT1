# Q176: from_hash — struct coercion via response shape

## Question
Starting from `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, can an unprivileged attacker supply the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in` so that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::AccessTokenResponse.from_hash`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
