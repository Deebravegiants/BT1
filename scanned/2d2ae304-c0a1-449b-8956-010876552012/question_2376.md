# Q2376: temp — nil means valid via associated_user id

## Question
If an unprivileged attacker submits the `associated_user.id` from the token response, interpolated into the session id to `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block, does `Auth::Session.temp` end up acting on a value that was never authenticated, because `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.temp`
- Entrypoint: `Session.temp(shop:, access_token:)`, which swaps `Context.active_session` around a block
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
