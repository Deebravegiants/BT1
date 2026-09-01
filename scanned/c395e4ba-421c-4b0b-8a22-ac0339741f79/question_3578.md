# Q3578: get_path — dynamic dispatch on response data via primary key value

## Question
Starting from `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids, can an unprivileged attacker supply the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path so that `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Rest::Base.get_path`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the primary-key value, which decides `deduce_write_verb` between `:put` and `:post` and is interpolated into the write path
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
