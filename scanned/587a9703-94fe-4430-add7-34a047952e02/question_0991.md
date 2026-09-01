# Q991: temp — identity built by interpolation via caller-supplied id

## Question
Can the `id:` keyword, which lets a session be constructed under any storage key, supplied by an unprivileged attacker at `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block, make `Auth::Session.temp` and the code consuming its result disagree, given that session ids are string concatenations of values that may contain the delimiter? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
