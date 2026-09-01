# Q3212: session_id_from_shopify_id_token — key is predictable via chosen cookie value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, makes `SessionUtils.session_id_from_shopify_id_token` return a result the caller treats as authenticated, given that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
