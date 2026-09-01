# Q3625: setup? — host header decoupled from connection via scope default

## Question
Is there a reachable state in which an unprivileged attacker, controlling the default `scope`, used by `begin_auth` whenever no override is passed at `setup?`, which only checks that four strings are non-empty, makes `Context.setup?` return a result the caller treats as authenticated, given that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `activate_session` is cleared at the end of a request cycle so a pooled thread cannot serve a stale tenant
