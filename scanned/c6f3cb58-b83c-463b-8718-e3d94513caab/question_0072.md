# Q72: from_hash — struct coercion via expires_in absent

## Question
Does `Oauth::AccessTokenResponse.from_hash` collapse two distinct identities into one when an unprivileged attacker submits an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response? Show that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
