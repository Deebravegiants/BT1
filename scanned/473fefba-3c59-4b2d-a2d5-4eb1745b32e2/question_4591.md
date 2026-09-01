# Q4591: shop — claim trusted as identity via Bearer prefix games

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, makes `JwtPayload#shop` return a result the caller treats as authenticated, given that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
