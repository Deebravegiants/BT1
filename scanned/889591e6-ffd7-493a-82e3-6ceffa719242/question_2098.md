# Q2098: load_rest_resources — host header decoupled from connection via thread-local session

## Question
Trace `Context.load_rest_resources` from `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader with the active session under concurrency, where a request handler runs on a pooled thread: because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the active session under concurrency, where a request handler runs on a pooled thread
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
