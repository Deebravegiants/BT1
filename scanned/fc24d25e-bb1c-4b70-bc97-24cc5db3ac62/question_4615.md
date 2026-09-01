# Q4615: shopify_user_id — unanchored substitution via sid claim

## Question
Does `JwtPayload#shopify_user_id` collapse two distinct identities into one when an unprivileged attacker submits the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`? Show that `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: the optional `sid` claim, which identifies the Shopify-side session and is stored but never used to bind the derived identity
- Exploit idea: `gsub("https://","")` removes every occurrence anywhere in the claim, not a leading scheme
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
