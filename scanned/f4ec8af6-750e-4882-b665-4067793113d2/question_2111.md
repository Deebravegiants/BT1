# Q2111: expired? — temp restores unconditionally via caller-supplied id

## Question
Can the `id:` keyword, which lets a session be constructed under any storage key, supplied by an unprivileged attacker at `expired?`, which returns false whenever `@expires` is nil, make `Auth::Session#expired?` and the code consuming its result disagree, given that the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
