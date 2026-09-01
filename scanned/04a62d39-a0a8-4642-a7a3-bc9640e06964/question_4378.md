# Q4378: set_property — template selection is textual via original_state diff

## Question
If an unprivileged attacker submits the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends to `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, does `Rest::Base#set_property` end up acting on a value that was never authenticated, because `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
