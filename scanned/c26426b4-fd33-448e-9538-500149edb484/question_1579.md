# Q1579: get_path_ids — read-only filter applied late via original_state diff

## Question
Can the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends, supplied by an unprivileged attacker at `get_path_ids`, which enumerates the id placeholders a path template requires, make `Rest::Base.get_path_ids` and the code consuming its result disagree, given that the read-only filter runs at serialisation time, after values have already been set on the instance? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
