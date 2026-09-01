# Q5271: initialize — unanchored substitution via Bearer prefix games

## Question
Can an unprivileged attacker reach `JwtPayload#initialize` through `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header while supplying an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix, so that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#initialize`
- Entrypoint: `ShopifyAPI::Auth::JwtPayload.new(token)`, reached from every embedded request carrying an `Authorization: Bearer <id_token>` header
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
