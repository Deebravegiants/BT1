# Q3972: offline_session_id — interpolation collision via cookie plus token

## Question
If an unprivileged attacker submits a request presenting both a cookie and an id token with conflicting shops to `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, does `SessionUtils.offline_session_id` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
