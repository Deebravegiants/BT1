# Q3187: begin_auth — session id derived from callback input via empty state

## Question
Does `Oauth.begin_auth` collapse two distinct identities into one when an unprivileged attacker submits an empty-string `state` in both cookie and query, so the `state == auth_query.state` comparison trivially succeeds at `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`? Show that `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: an empty-string `state` in both cookie and query, so the `state == auth_query.state` comparison trivially succeeds
- Exploit idea: `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
