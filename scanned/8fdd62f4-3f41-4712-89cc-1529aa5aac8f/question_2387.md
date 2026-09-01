# Q2387: method_missing — template selection is textual via params hash

## Question
Can an unprivileged attacker reach `Rest::Base#method_missing` through `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access while supplying the `params:` hash, forwarded as the outgoing query string, so that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: the `params:` hash, forwarded as the outgoing query string
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
