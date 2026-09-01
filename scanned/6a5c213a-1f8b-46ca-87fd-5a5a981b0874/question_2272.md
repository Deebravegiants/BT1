# Q2272: == — equality omits the token via caller-supplied id

## Question
Can the `id:` keyword, which lets a session be constructed under any storage key, supplied by an unprivileged attacker at `Session#==`, used by callers to decide whether a stored session matches, make `Auth::Session#==` and the code consuming its result disagree, given that `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#==`
- Entrypoint: `Session#==`, used by callers to decide whether a stored session matches
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: `Session#==` compares many fields; a caller using it to decide sameness may treat two sessions with different credentials as equal
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
