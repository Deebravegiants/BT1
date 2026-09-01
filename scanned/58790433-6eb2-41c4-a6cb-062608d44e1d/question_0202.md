# Q202: from_hash — no grant cross-check via associated_user id type

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, makes `Oauth::AccessTokenResponse.from_hash` return a result the caller treats as authenticated, given that the returned `scope` is stored without comparing it to the scope the authorization actually requested? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key
- Exploit idea: the returned `scope` is stored without comparing it to the scope the authorization actually requested
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
