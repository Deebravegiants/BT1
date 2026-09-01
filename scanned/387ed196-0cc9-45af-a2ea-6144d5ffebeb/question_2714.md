# Q2714: copy_attributes_from — equality omits the token via copy across identities

## Question
Trace `Auth::Session#copy_attributes_from` from `copy_attributes_from(other)`, which overwrites every attribute except `id` with a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`: because `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#copy_attributes_from`
- Entrypoint: `copy_attributes_from(other)`, which overwrites every attribute except `id`
- Attacker controls: a `copy_attributes_from` call that moves another shop's `shop` and `access_token` onto a session keeping its own `id`
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
