# Q4966: shop — unanchored substitution via Bearer prefix games

## Question
If an unprivileged attacker submits an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix to `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, does `JwtPayload#shop` end up acting on a value that was never authenticated, because `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
