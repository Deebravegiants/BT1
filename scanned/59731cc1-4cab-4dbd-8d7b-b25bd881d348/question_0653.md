# Q653: online_token? — struct coercion via associated_user id type

## Question
Does `Oauth::AccessTokenResponse#online_token?` collapse two distinct identities into one when an unprivileged attacker submits an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`? Show that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
