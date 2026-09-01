# Q3448: copy_attributes_from — nil means valid via caller-supplied id

## Question
Can the `id:` keyword, which lets a session be constructed under any storage key, supplied by an unprivileged attacker at `copy_attributes_from(other)`, which overwrites every attribute except `id`, make `Auth::Session#copy_attributes_from` and the code consuming its result disagree, given that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
