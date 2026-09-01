# Q3443: offline_session_id — interpolation collision via empty token

## Question
Is there a reachable state in which an unprivileged attacker, controlling an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, makes `SessionUtils.offline_session_id` return a result the caller treats as authenticated, given that string concatenation with `_` makes distinct identities collide? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
