# Q3992: offline_session_id — caller decides identity shape via non-embedded config

## Question
Does `SessionUtils.offline_session_id` collapse two distinct identities into one when an unprivileged attacker submits an app configured `is_embedded: false`, where the cookie is the only accepted credential at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation? Show that the `online` boolean, not the token, selects which identity is loaded, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
