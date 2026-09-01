# Q46: online_token? — missing expiry means eternal via scope mismatch

## Question
Can a `scope` string that does not match what the app requested at `begin_auth`, supplied by an unprivileged attacker at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, make `Oauth::AccessTokenResponse#online_token?` and the code consuming its result disagree, given that an absent `expires_in` yields a session that never reports expiry? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: a `scope` string that does not match what the app requested at `begin_auth`
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
