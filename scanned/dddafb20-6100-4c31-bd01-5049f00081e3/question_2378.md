# Q2378: setup? — host header decoupled from connection via thread-local session

## Question
Trace `Context.setup?` from `setup?`, which only checks that four strings are non-empty with the active session under concurrency, where a request handler runs on a pooled thread: because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
