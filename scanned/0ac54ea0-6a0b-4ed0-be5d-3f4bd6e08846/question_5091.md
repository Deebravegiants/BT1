# Q5091: decode_token — rotation widens acceptance via dest without scheme

## Question
Does `JwtPayload#decode_token` collapse two distinct identities into one when an unprivileged attacker submits a `dest` claim that is not `https://<shop>` (no scheme, a path, a port, or multiple `https://` occurrences the unanchored `gsub` all strip) at the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`? Show that the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a `dest` claim that is not `https://<shop>` (no scheme, a path, a port, or multiple `https://` occurrences the unanchored `gsub` all strip)
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
