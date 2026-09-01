# Q3476: session_id_from_shopify_id_token — unauthenticated bytes become the key via online flag flip

## Question
Can control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token, supplied by an unprivileged attacker at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, make `SessionUtils.session_id_from_shopify_id_token` and the code consuming its result disagree, given that the cookie value is returned as the session id with no MAC, no signature and no shop binding? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
