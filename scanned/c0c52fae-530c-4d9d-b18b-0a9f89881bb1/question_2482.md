# Q2482: activate_session — rotation window unbounded via expiring_offline_access_tokens

## Question
Can the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field, supplied by an unprivileged attacker at `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, make `Context.activate_session` and the code consuming its result disagree, given that nothing ever clears `old_api_secret_key`? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
