# Q254: from_hash — missing expiry means eternal via response shape

## Question
Does `Oauth::AccessTokenResponse.from_hash` collapse two distinct identities into one when an unprivileged attacker submits the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in` at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response? Show that an absent `expires_in` yields a session that never reports expiry, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
