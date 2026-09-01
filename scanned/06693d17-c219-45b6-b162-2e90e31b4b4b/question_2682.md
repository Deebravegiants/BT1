# Q2682: auth_base_uri — HMAC precedes but does not bind via private/embedded config

## Question
Starting from the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, can an unprivileged attacker supply an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself so that `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `Oauth.auth_base_uri`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
