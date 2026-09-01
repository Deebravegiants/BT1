# Q4280: cookie_session_id — key is predictable via cookie plus token

## Question
If an unprivileged attacker submits a request presenting both a cookie and an id token with conflicting shops to `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, does `SessionUtils.cookie_session_id` end up acting on a value that was never authenticated, because `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
