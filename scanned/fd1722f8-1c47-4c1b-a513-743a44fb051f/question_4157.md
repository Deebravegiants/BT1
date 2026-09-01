# Q4157: validate_auth_callback — session id derived from callback input via stale timestamp

## Question
Is there a reachable state in which an unprivileged attacker, controlling a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now` at `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, makes `Oauth.validate_auth_callback` return a result the caller treats as authenticated, given that `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`
- Exploit idea: `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
