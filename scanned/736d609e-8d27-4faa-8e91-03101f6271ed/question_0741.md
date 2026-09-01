# Q741: online_token? — missing expiry means eternal via expires_in absent

## Question
Is there a reachable state in which an unprivileged attacker, controlling an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, makes `Oauth::AccessTokenResponse#online_token?` return a result the caller treats as authenticated, given that an absent `expires_in` yields a session that never reports expiry? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: an omitted `expires_in`, leaving `Session#expires` nil and `expired?` permanently false
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
