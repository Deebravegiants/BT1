# Q3102: cookie_session_id — key is predictable via chosen cookie value

## Question
Starting from `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, can an unprivileged attacker supply the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check so that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `SessionUtils.cookie_session_id`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
