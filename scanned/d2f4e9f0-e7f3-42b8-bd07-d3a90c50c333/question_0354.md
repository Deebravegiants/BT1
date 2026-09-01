# Q354: from_hash — no grant cross-check via expires_in absent

## Question
Can an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false, supplied by an unprivileged attacker at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, make `Oauth::AccessTokenResponse.from_hash` and the code consuming its result disagree, given that the returned `scope` is stored without comparing it to the scope the authorization actually requested? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: the returned `scope` is stored without comparing it to the scope the authorization actually requested
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
