# Q4663: set_property — query forwarded verbatim via pagination cursors

## Question
Starting from `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, can an unprivileged attacker supply `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request so that `params:` is passed through to the outgoing query with the merchant's token attached? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Rest::Base#set_property`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: stub a response whose JSON keys collide with internal methods and assert `create_instance` cannot overwrite the instance's session or client
