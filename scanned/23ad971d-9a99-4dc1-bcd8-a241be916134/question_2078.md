# Q2078: to_hash — dynamic dispatch on response data via params hash

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `params:` hash, forwarded as the outgoing query string at `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`, makes `Rest::Base#to_hash` return a result the caller treats as authenticated, given that `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#to_hash`
- Entrypoint: `to_hash(saving)`, which walks `instance_variables` and filters `read_only_attributes`
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
