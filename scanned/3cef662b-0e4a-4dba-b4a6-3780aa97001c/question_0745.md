# Q745: load_rest_resources — host header decoupled from connection via expiring_offline_access_tokens

## Question
If an unprivileged attacker submits the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field to `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader, does `Context.load_rest_resources` end up acting on a value that was never authenticated, because with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.load_rest_resources`
- Entrypoint: `load_rest_resources(api_version:)`, which builds a filesystem path from the version string and drives a Zeitwerk loader
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
