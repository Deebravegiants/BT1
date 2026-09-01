# Q2636: shop — leeway on both ends via dest with embedded separator

## Question
Can a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator, supplied by an unprivileged attacker at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, make `JwtPayload#shop` and the code consuming its result disagree, given that a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
