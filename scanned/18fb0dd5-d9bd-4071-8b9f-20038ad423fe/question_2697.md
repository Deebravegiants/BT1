# Q2697: offline_session_id — interpolation collision via online flag flip

## Question
Does `SessionUtils.offline_session_id` collapse two distinct identities into one when an unprivileged attacker submits control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation? Show that string concatenation with `_` makes distinct identities collide, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
