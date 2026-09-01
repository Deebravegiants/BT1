# Q3094: to_hash — query forwarded verbatim via ids hash

## Question
Can an unprivileged attacker reach `Rest::Base#to_hash` through `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes` while supplying the `ids:` hash passed to `base_find`, whose values are interpolated into the request path, so that `params:` is passed through to the outgoing query with the merchant's token attached, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `ids:` hash passed to `base_find`, whose values are interpolated into the request path
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
