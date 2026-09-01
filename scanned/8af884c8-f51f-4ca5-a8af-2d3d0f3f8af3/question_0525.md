# Q525: host_name — setup? is a presence check via scope default

## Question
Can an unprivileged attacker reach `Context.host_name` through `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI` while supplying the default `scope`, used by `begin_auth` whenever no override is passed, so that `setup?` proves four strings are non-empty, not that any of them is well-formed, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the default `scope`, used by `begin_auth` whenever no override is passed
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
