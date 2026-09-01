# Q2274: setup? — rotation window unbounded via old_api_secret_key

## Question
Is there a reachable state in which an unprivileged attacker, controlling `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted at `setup?`, which only checks that four strings are non-empty, makes `Context.setup?` return a result the caller treats as authenticated, given that nothing ever clears `old_api_secret_key`? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
