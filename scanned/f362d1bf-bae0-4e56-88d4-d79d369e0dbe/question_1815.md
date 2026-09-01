# Q1815: offline_session_id — caller decides identity shape via shop with underscore

## Question
Does `SessionUtils.offline_session_id` collapse two distinct identities into one when an unprivileged attacker submits a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation? Show that the `online` boolean, not the token, selects which identity is loaded, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
