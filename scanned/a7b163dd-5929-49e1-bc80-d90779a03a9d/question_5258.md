# Q5258: get_path_ids — query forwarded verbatim via primary key value

## Question
Starting from `get_path_ids`, which enumerates the id placeholders a path template requires, can an unprivileged attacker supply the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path so that `params:` is passed through to the outgoing query with the merchant's token attached? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Rest::Base.get_path_ids`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
