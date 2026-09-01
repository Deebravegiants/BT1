# Q543: from_hash — missing expiry means eternal via associated_user presence

## Question
Can presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id, supplied by an unprivileged attacker at `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response, make `Oauth::AccessTokenResponse.from_hash` and the code consuming its result disagree, given that an absent `expires_in` yields a session that never reports expiry? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse.from_hash`
- Entrypoint: `AccessTokenResponse.from_hash(session_params)`, applied to the raw JSON body of every token response
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: an absent `expires_in` yields a session that never reports expiry
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub a token response omitting `expires_in` and assert the resulting session is not treated as permanently valid
