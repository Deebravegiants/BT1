# Q4693: to_hash — cursor trusted via original_state diff

## Question
If an unprivileged attacker submits the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends to `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, does `Rest::Base#to_hash` end up acting on a value that was never authenticated, because page-info cursors from a response are replayed into the next authenticated request without validation? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
