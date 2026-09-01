# Q4423: shopify_user_id — unanchored substitution via missing claims

## Question
Is there a reachable state in which an unprivileged attacker, controlling a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, makes `JwtPayload#shopify_user_id` return a result the caller treats as authenticated, given that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a token omitting `sid`, `jti` or `sub`, exercising the `T.let(..., T.nilable(String))` paths
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
