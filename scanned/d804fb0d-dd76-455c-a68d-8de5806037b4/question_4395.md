# Q4395: copy_attributes_from — nil means valid via concurrent temp

## Question
Is there a reachable state in which an unprivileged attacker, controlling overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session at `copy_attributes_from(other)`, which overwrites every attribute except `id`, makes `Auth::Session#copy_attributes_from` return a result the caller treats as authenticated, given that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
