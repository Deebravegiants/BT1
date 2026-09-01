# Q415: jwt_session_id — no shop cross-check via Bearer interior match

## Question
Does `SessionUtils.jwt_session_id` collapse two distinct identities into one when an unprivileged attacker submits an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation? Show that nothing asserts the loaded session's `shop` matches the shop authenticated by this request, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
