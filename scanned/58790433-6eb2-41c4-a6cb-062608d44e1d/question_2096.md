# Q2096: copy_attributes_from — id and shop can disagree via caller-supplied id

## Question
If an unprivileged attacker submits the `id:` keyword, which lets a session be constructed under any storage key to `copy_attributes_from(other)`, which overwrites every attribute except `id`, does `Auth::Session#copy_attributes_from` end up acting on a value that was never authenticated, because `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
