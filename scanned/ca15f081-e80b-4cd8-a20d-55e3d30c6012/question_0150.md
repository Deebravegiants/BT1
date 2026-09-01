# Q150: from_hash — struct coercion via associated_user id type

## Question
If an unprivileged attacker submits an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key to `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, does `Oauth::AccessTokenResponse.from_hash` end up acting on a value that was never authenticated, because `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: an `associated_user.id` whose type or value changes the `"#{shop}_#{id}"` key
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
