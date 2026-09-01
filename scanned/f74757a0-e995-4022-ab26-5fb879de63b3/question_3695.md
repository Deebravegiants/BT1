# Q3695: get_path_ids — cursor trusted via primary key value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path at `get_path_ids`, which enumerates the id placeholders a path template requires, makes `Rest::Base.get_path_ids` return a result the caller treats as authenticated, given that page-info cursors from a response are replayed into the next authenticated request without validation? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
