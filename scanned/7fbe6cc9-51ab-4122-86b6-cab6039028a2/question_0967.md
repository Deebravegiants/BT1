# Q967: to_hash — path interpolation from ids via has_many element class

## Question
Starting from `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, can an unprivileged attacker supply the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated so that ids are concatenated into the path template with no escaping or type check? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Rest::Base#to_hash`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
