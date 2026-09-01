# Q1228: shop — rotation widens acceptance via iss/dest mismatch

## Question
If an unprivileged attacker submits a token whose `iss` and `dest` claims name different shops, which the constructor never compares to `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`, does `JwtPayload#shop` end up acting on a value that was never authenticated, because the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a token whose `iss` and `dest` claims name different shops, which the constructor never compares
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
