# Q3453: admin_session_token? — type assumptions via own-shop id token

## Question
Does `JwtPayload#admin_session_token?` collapse two distinct identities into one when an unprivileged attacker submits a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app at `admin_session_token?`, a bare `@iss.end_with?("/admin")` check? Show that `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app
- Exploit idea: `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
