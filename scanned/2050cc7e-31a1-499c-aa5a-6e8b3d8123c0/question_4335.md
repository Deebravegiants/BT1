# Q4335: shop — rotation widens acceptance via aud edge

## Question
Does `JwtPayload#shop` collapse two distinct identities into one when an unprivileged attacker submits an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key) at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`? Show that the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `aud` claim that equals `Context.api_key` by type coercion rather than value (array form, numeric key)
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
