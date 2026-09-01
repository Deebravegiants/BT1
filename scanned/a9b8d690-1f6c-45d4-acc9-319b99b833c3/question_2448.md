# Q2448: admin_session_token? — leeway on both ends via Bearer prefix games

## Question
Trace `JwtPayload#admin_session_token?` from `admin_session_token?`, a bare `@iss.end_with?("/admin")` check with an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix: because a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#admin_session_token?`
- Entrypoint: `admin_session_token?`, a bare `@iss.end_with?("/admin")` check
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` in `SessionUtils` removes an interior occurrence, not just the prefix
- Exploit idea: a symmetric 10-second leeway is applied to `exp` and `nbf`, widening the replay window at both boundaries
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
