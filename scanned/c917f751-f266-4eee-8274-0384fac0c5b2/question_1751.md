# Q1751: session_id_from_shopify_id_token — fallback weakens the strong path via non-embedded config

## Question
Starting from `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, can an unprivileged attacker supply an app configured `is_embedded: false`, where the cookie is the only accepted credential so that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `SessionUtils.session_id_from_shopify_id_token`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
