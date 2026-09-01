# Q1326: == — id and shop can disagree via scope string

## Question
If an unprivileged attacker submits the `scope` string from the token response, parsed by `AuthScopes` with no validation to `Session#==`, used by callers to decide whether a stored session matches, does `Auth::Session#==` end up acting on a value that was never authenticated, because `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: the `scope` string from the token response, parsed by `AuthScopes` with no validation
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
