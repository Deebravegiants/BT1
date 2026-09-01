# Q890: online_token? — missing expiry means eternal via associated_user id type

## Question
Starting from `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, can an unprivileged attacker supply an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key so that an absent `expires_in` yields a session that never reports expiry? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::AccessTokenResponse#online_token?`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
