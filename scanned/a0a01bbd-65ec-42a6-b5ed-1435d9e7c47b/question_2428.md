# Q2428: temp — identity built by interpolation via online/offline flip

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?` at `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block, makes `Auth::Session.temp` return a result the caller treats as authenticated, given that session ids are string concatenations of values that may contain the delimiter? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
