# Q124: from_hash — missing expiry means eternal via expires_in absent

## Question
Trace `Oauth::AccessTokenResponse.from_hash` from `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response with an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false: because an absent `expires_in` yields a session that never reports expiry, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the stored `scope` is compared against the scope requested at `begin_auth`
