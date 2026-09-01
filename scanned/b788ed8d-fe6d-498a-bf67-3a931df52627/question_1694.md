# Q1694: initialize — temp restores unconditionally via online/offline flip

## Question
Can an unprivileged attacker reach `Auth::Session#initialize` through `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable while supplying an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`, so that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - theft of a merchant's refresh token, granting durable access after rotation?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#initialize`
- Entrypoint: `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
