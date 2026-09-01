# Q3316: from — id and shop can disagree via caller-supplied id

## Question
Trace `Auth::Session.from` from `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"` with the `id:` keyword, which lets a session be constructed under any storage key: because `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session.from`
- Entrypoint: `Session.from(shop:, access_token_response:)`, which mints `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"`
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
