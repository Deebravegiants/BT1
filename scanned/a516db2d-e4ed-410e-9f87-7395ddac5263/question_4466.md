# Q4466: set_property — template selection is textual via nested has_many/has_one

## Question
Can an unprivileged attacker reach `Rest::Base#set_property` through `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data while supplying nested objects whose class is resolved from the attribute name, so that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: nested objects whose class is resolved from the attribute name
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
