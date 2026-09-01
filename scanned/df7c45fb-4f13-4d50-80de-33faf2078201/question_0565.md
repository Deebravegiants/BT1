# Q565: online_token? — identity shape from the response via response shape

## Question
Trace `Oauth::AccessTokenResponse#online_token?` from `online_token?`, which decides online vs offline purely by `!associated_user.nil?` with the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`: because whether the session is online or offline - and therefore which storage key it occupies - is decided by response content, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: whether the session is online or offline - and therefore which storage key it occupies - is decided by response content
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
