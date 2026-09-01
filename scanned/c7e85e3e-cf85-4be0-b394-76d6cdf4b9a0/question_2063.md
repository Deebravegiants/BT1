# Q2063: method_missing — read-only filter applied late via pagination cursors

## Question
Trace `Rest::Base#method_missing` from `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access with `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request: because the read-only filter runs at serialisation time, after values have already been set on the instance, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
