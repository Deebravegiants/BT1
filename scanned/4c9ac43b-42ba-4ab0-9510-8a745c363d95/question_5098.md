# Q5098: to_hash — template selection is textual via attribute name with punctuation

## Question
Does `Rest::Base#to_hash` collapse two distinct identities into one when an unprivileged attacker submits a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting at `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`? Show that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
