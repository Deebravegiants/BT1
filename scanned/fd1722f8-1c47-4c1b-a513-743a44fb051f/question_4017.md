# Q4017: == — equality omits the token via concurrent temp

## Question
Is there a reachable state in which an unprivileged attacker, controlling overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session at `Session#==`, used by callers to decide whether a stored session matches, makes `Auth::Session#==` return a result the caller treats as authenticated, given that `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
