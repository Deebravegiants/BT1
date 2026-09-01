# Q1387: save — query forwarded verbatim via primary key value

## Question
Starting from `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`, can an unprivileged attacker supply the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path so that `params:` is passed through to the outgoing query with the merchant's token attached? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Rest::Base#save`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#save`
- Entrypoint: `save(update_object:)`, which chooses verb and path via `deduce_write_verb` and `deduce_write_path`
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
