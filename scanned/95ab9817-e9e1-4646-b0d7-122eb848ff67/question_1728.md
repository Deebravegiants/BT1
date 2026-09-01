# Q1728: host_name — setup? is a presence check via rest_disabled

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `rest_disabled` flag, which decides whether the REST client raises at `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, makes `Context.host_name` return a result the caller treats as authenticated, given that `setup?` proves four strings are non-empty, not that any of them is well-formed? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: `setup?` proves four strings are non-empty, not that any of them is well-formed
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
