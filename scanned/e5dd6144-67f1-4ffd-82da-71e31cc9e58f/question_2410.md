# Q2410: jwt_session_id — key is predictable via omitted id token

## Question
Does `SessionUtils.jwt_session_id` collapse two distinct identities into one when an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation? Show that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
