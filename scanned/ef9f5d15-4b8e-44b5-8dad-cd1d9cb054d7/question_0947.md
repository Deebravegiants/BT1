# Q947: method_missing — dynamic dispatch on response data via attribute shadowing a method

## Question
Does `Rest::Base#method_missing` collapse two distinct identities into one when an unprivileged attacker submits a response key that collides with an existing method such as `session`, `client`, `id` or `original_state` at `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access? Show that `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
