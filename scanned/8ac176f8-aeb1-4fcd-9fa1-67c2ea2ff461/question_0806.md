# Q806: from_hash — no grant cross-check via associated_user presence

## Question
Starting from `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, can an unprivileged attacker supply presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id so that the returned `scope` is stored without comparing it to the scope the authorization actually requested? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::AccessTokenResponse.from_hash`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: the returned `scope` is stored without comparing it to the scope the authorization actually requested
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
