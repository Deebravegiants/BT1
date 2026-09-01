# Q2305: decode_token — no iss/dest binding via missing claims

## Question
Does `JwtPayload#decode_token` collapse two distinct identities into one when an unprivileged attacker submits a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths at the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`? Show that the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths
- Exploit idea: the constructor validates `aud` only; nothing asserts `iss` and `dest` describe the same shop
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
