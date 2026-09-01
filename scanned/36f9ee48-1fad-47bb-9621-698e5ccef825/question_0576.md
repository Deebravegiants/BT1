# Q576: shop — unanchored substitution via iss suffix

## Question
Does `JwtPayload#shop` collapse two distinct identities into one when an unprivileged attacker submits an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?` at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`? Show that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
