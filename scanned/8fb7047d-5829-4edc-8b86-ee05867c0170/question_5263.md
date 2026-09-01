# Q5263: base_find — cursor trusted via primary key value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path at `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`, makes `Rest::Base.base_find` return a result the caller treats as authenticated, given that page-info cursors from a response are replayed into the next authenticated request without validation? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
