# Q1726: initialize — identity built by interpolation via concurrent temp

## Question
Can overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session, supplied by an unprivileged attacker at `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable, make `Auth::Session#initialize` and the code consuming its result disagree, given that session ids are string concatenations of values that may contain the delimiter? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#initialize`
- Entrypoint: `Session.new(shop:, id:, state:, access_token:, scope:, ...)`, whose `id` defaults to `SecureRandom.uuid` but is caller-overridable
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
