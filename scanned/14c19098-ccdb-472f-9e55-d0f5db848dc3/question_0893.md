# Q893: host_name — thread-local, not request-local via old_api_secret_key

## Question
Can `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted, supplied by an unprivileged attacker at `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`, make `Context.host_name` and the code consuming its result disagree, given that `active_session` is thread-local; on a pooled server a session can outlive the request that set it? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.host_name`
- Entrypoint: `host_name` / `host_scheme`, which parse `Context.host` (defaulted from `ENV['HOST']`) with `URI`
- Attacker controls: `old_api_secret_key`, which permanently widens the set of signatures and tokens accepted
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
