# Q2363: initialize — nil means valid via caller-supplied id

## Question
Can the `id:` keyword, which lets a session be constructed under any storage key, supplied by an unprivileged attacker at `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable, make `Auth::Session#initialize` and the code consuming its result disagree, given that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#initialize`
- Entrypoint: `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
