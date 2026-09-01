# Q1511: jwt_session_id — fallback weakens the strong path via shop casing

## Question
Is there a reachable state in which an unprivileged attacker, controlling a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, makes `SessionUtils.jwt_session_id` return a result the caller treats as authenticated, given that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
