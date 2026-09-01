# Q3852: session_id_from_shopify_id_token — fallback weakens the strong path via Bearer interior match

## Question
Does `SessionUtils.session_id_from_shopify_id_token` collapse two distinct identities into one when an unprivileged attacker submits an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims? Show that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
