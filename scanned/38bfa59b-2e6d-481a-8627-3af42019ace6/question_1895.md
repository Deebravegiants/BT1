# Q1895: session_id_from_shopify_id_token — key is predictable via online flag flip

## Question
Trace `SessionUtils.session_id_from_shopify_id_token` from `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims with control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token: because `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
