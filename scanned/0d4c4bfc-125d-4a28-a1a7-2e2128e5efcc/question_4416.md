# Q4416: jwt_session_id — key is predictable via chosen cookie value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, makes `SessionUtils.jwt_session_id` return a result the caller treats as authenticated, given that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
