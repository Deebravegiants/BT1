# Q3394: activate_session — setup? is a presence check via host / ENV['HOST']

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses at `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`, makes `Context.activate_session` return a result the caller treats as authenticated, given that `setup?` proves four strings are non-empty, not that any of them is well-formed? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `host` value, parsed by `host_name`/`host_scheme` and used to build redirect URIs and webhook callback addresses
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
