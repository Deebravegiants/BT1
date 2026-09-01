# Q1607: jwt_session_id — caller decides identity shape via online flag flip

## Question
Can control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token, supplied by an unprivileged attacker at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, make `SessionUtils.jwt_session_id` and the code consuming its result disagree, given that the `online` boolean, not the token, selects which identity is loaded? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
