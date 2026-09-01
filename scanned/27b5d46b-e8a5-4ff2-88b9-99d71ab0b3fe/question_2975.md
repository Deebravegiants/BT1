# Q2975: temp — copy preserves the key via associated_user id

## Question
Can an unprivileged attacker reach `Auth::Session.temp` through `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block while supplying the `associated_user.id` from the token response, interpolated into the session id, so that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
