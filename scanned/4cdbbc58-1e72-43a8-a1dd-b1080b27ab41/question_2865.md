# Q2865: offline_session_id — fallback weakens the strong path via guessed offline key

## Question
Does `SessionUtils.offline_session_id` collapse two distinct identities into one when an unprivileged attacker submits a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation? Show that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
