# Q3185: activate_session — global identity, per-request requests via rest_disabled

## Question
Can an unprivileged attacker reach `Context.activate_session` through `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar` while supplying the `rest_disabled` flag, which decides whether the REST client raises, so that one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.activate_session`
- Entrypoint: `Context.activate_session(session)` and `Context.active_session`, backed by a `Concurrent::ThreadLocalVar`
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: one process-wide `Context` serves every shop, so any leakage between requests crosses a tenant boundary
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
