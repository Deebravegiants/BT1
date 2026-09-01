# Q4074: initialize — temp restores unconditionally via scope string

## Question
Can an unprivileged attacker reach `Auth::Session#initialize` through `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable while supplying the `scope` string from the token response, parsed by `AuthScopes` with no validation, so that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - theft of a merchant's refresh token, granting durable access after rotation?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#initialize`
- Entrypoint: `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable
- Attacker controls: the `scope` string from the token response, parsed by `AuthScopes` with no validation
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
