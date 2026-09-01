# Q572: auth_base_uri — session id derived from callback input via attacker-signed callback

## Question
Trace `Oauth.auth_base_uri` from the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` with a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app: because `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app
- Exploit idea: `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
