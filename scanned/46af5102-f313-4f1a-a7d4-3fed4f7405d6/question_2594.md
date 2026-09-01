# Q2594: == — nil means valid via copy across identities

## Question
Can a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`, supplied by an unprivileged attacker at `Session#==`, used by callers to decide whether a stored session matches, make `Auth::Session#==` and the code consuming its result disagree, given that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
