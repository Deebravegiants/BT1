# Q4761: shop — type assumptions via dest with embedded separator

## Question
Starting from `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, can an unprivileged attacker supply a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator so that `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `JwtPayload#shop`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator
- Exploit idea: `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
