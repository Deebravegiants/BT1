# Q2491: set_property — method shadowing via primary key value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, makes `Rest::Base#set_property` return a result the caller treats as authenticated, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
