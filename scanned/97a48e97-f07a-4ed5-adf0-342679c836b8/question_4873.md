# Q4873: method_missing — query forwarded verbatim via ids hash

## Question
Starting from `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access, can an unprivileged attacker supply the `ids:` hash passed to `base_find`, whose values are interpolated into the request path so that `params:` is passed through to the outgoing query with the merchant's token attached? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Rest::Base#method_missing`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#method_missing`
- Entrypoint: `method_missing(meth_id, val = nil)`, which turns arbitrary reads and writes into property access
- Attacker controls: the `ids:` hash passed to `base_find`, whose values are interpolated into the request path
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
