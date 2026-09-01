# Q4339: initialize — copy preserves the key via associated_user id

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `associated_user.id` from the token response, interpolated into the session id at `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable, makes `Auth::Session#initialize` return a result the caller treats as authenticated, given that `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#initialize`
- Entrypoint: `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `copy_attributes_from` overwrites the shop and token while keeping the id, so a key silently starts pointing at a different tenant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
