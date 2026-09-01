# Q3042: setup? — thread-local, not request-local via api_host vs session.shop

## Question
Can the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`, supplied by an unprivileged attacker at `setup?`, which only checks that four strings are non-empty, make `Context.setup?` and the code consuming its result disagree, given that `active_session` is thread-local; on a pooled server a session can outlive the request that set it? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `api_host` setting, which splits the connection host from the `Host` header taken from `session.shop`
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
