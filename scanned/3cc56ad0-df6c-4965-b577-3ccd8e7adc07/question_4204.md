# Q4204: shop — leeway on both ends via expired but rotated

## Question
Can a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch, supplied by an unprivileged attacker at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, make `JwtPayload#shop` and the code consuming its result disagree, given that a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
