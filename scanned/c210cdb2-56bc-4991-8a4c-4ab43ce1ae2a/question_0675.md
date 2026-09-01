# Q675: online_token? — missing expiry means eternal via associated_user presence

## Question
If an unprivileged attacker submits presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id to `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, does `Oauth::AccessTokenResponse#online_token?` end up acting on a value that was never authenticated, because an absent `expires_in` yields a session that never reports expiry? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
