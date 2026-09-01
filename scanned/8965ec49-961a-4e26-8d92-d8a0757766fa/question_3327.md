# Q3327: temp — identity built by interpolation via concurrent temp

## Question
Does `Auth::Session.temp` collapse two distinct identities into one when an unprivileged attacker submits overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session at `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block? Show that session ids are string concatenations of values that may contain the delimiter, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
