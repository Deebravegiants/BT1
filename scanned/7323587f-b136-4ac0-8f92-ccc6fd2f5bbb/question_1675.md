# Q1675: get_path — template selection is textual via session argument

## Question
Does `Rest::Base.get_path` collapse two distinct identities into one when an unprivileged attacker submits the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries at `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids? Show that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the `session:` argument threaded through `base_find` and `save`, which decides whose access token the resource call carries
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
