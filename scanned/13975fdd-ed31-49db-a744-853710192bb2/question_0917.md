# Q917: auth_base_uri — private-app guard ordering via private/embedded config

## Question
Can an unprivileged attacker reach `Oauth.auth_base_uri` through the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` while supplying an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself, so that `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host, breaking the requirement that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself
- Exploit idea: `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
