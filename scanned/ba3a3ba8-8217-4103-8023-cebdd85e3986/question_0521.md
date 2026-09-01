# Q521: online_token? — no grant cross-check via associated_user presence

## Question
If an unprivileged attacker submits presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id to `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, does `Oauth::AccessTokenResponse#online_token?` end up acting on a value that was never authenticated, because the returned `scope` is stored without comparing it to the scope the authorization actually requested? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: the returned `scope` is stored without comparing it to the scope the authorization actually requested
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
