# Q304: online_token? — missing expiry means eternal via response shape

## Question
If an unprivileged attacker submits the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in` to `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, does `Oauth::AccessTokenResponse#online_token?` end up acting on a value that was never authenticated, because an absent `expires_in` yields a session that never reports expiry? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
