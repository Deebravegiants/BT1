# Q475: online_token? — no grant cross-check via response shape

## Question
Is there a reachable state in which an unprivileged attacker, controlling the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in` at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, makes `Oauth::AccessTokenResponse#online_token?` return a result the caller treats as authenticated, given that the returned `scope` is stored without comparing it to the scope the authorization actually requested? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: the returned `scope` is stored without comparing it to the scope the authorization actually requested
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
