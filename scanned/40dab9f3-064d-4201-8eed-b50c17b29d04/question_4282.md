# Q4282: get_path — dynamic dispatch on response data via attribute shadowing a method

## Question
Trace `Rest::Base.get_path` from `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids with a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`: because `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: a response key that collides with an existing method such as `session`, `client`, `id` or `original_state`
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
