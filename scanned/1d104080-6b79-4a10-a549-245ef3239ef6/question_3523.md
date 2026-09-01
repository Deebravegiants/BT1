# Q3523: to_hash — query forwarded verbatim via original_state diff

## Question
Does `Rest::Base#to_hash` collapse two distinct identities into one when an unprivileged attacker submits the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends at `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`? Show that `params:` is passed through to the outgoing query with the merchant's token attached, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
