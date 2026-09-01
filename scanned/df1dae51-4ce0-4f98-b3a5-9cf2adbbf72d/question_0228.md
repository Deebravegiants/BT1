# Q228: from_hash — struct coercion via associated_user presence

## Question
Can presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id, supplied by an unprivileged attacker at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, make `Oauth::AccessTokenResponse.from_hash` and the code consuming its result disagree, given that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
