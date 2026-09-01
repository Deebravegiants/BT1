# Q5398: to_hash — read-only filter applied late via ids hash

## Question
Starting from `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, can an unprivileged attacker supply the `ids:` hash passed to `base_find`, whose values are interpolated into the request path so that the read-only filter runs at serialisation time, after values have already been set on the instance? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Rest::Base#to_hash`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `ids:` hash passed to `base_find`, whose values are interpolated into the request path
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
