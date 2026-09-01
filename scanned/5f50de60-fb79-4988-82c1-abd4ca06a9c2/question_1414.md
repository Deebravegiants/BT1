# Q1414: decode_token — unanchored substitution via own-shop id token

## Question
Can an unprivileged attacker reach `JwtPayload#decode_token` through the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')` while supplying a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app, so that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#decode_token`
- Entrypoint: the private `decode_token`, a `JWT.decode(token, secret, true, leeway: 10, algorithm: 'HS256')`
- Attacker controls: a genuine session token issued to the attacker's own shop, signed with the same `api_secret_key` that serves every install of the app
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
