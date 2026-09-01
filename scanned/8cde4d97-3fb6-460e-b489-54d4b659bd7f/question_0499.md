# Q499: online_token? — struct coercion via scope mismatch

## Question
Does `Oauth::AccessTokenResponse#online_token?` collapse two distinct identities into one when an unprivileged attacker submits a `scope` string that does not match what the app requested at `begin_auth` at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`? Show that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: a `scope` string that does not match what the app requested at `begin_auth`
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
