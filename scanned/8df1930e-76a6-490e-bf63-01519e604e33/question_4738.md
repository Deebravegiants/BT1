# Q4738: get_path — cursor trusted via session argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries at `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids, makes `Rest::Base.get_path` return a result the caller treats as authenticated, given that page-info cursors from a response are replayed into the next authenticated request without validation? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
