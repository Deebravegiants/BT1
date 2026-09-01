# Q2998: load_rest_resources — host header decoupled from connection via api_version string

## Question
Does `Context.load_rest_resources` collapse two distinct identities into one when an unprivileged attacker submits the `api_version` string, which becomes a directory path in `load_rest_resources` at `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader? Show that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `api_version` string, which becomes a directory path in `load_rest_resources`
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
