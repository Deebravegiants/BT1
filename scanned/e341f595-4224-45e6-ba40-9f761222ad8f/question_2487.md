# Q2487: shop — claim trusted as identity via iss suffix

## Question
Does `JwtPayload#shop` collapse two distinct identities into one when an unprivileged attacker submits an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?` at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`? Show that a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: an `iss` that merely ends with `/admin` (for example `https://evil.example/admin`), satisfying `admin_session_token?`
- Exploit idea: a claim is trusted to identify a tenant even though the signing secret is shared across every shop that installed the app
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: mint a token with `iss` = shop A and `dest` = shop B under the test secret, assert `JwtPayload#shop` and assert which shop the subsequent token exchange requests
