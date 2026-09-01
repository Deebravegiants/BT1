# Q1554: auth_base_uri — session id derived from callback input via extra query parameters

## Question
Can an unprivileged attacker reach `Oauth.auth_base_uri` through the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator` while supplying additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`), so that `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`)
- Exploit idea: `Session.from(shop: auth_query.shop, ...)` mints `offline_#{shop}` or `#{shop}_#{user.id}` from a value the attacker chose
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
