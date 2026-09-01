# Q258: load_rest_resources — global identity, per-request requests via scope default

## Question
Is there a reachable state in which an unprivileged attacker, controlling the default `scope`, used by `begin_auth` whenever no override is passed at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, makes `Context.load_rest_resources` return a result the caller treats as authenticated, given that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
