# Q3618: shop — unanchored substitution via expired but rotated

## Question
Is there a reachable state in which an unprivileged attacker, controlling a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, makes `JwtPayload#shop` return a result the caller treats as authenticated, given that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a token that fails under the current secret and is retried under `old_api_secret_key` by the rescue branch
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
