# Q279: online_token? — struct coercion via response shape

## Question
Is there a reachable state in which an unprivileged attacker, controlling the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in` at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, makes `Oauth::AccessTokenResponse#online_token?` return a result the caller treats as authenticated, given that `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: the JSON body of the token response, which decides `associated_user`, `expires_in`, `scope` and `refresh_token_expires_in`
- Exploit idea: `from_hash` coerces types, so unexpected shapes are either raised on or silently accepted depending on nilability
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
