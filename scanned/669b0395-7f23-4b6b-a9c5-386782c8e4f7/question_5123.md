# Q5123: get_path_ids — query forwarded verbatim via pagination cursors

## Question
Is there a reachable state in which an unprivileged attacker, controlling `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request at `get_path_ids`, which enumerates the id placeholders a path template requires, makes `Rest::Base.get_path_ids` return a result the caller treats as authenticated, given that `params:` is passed through to the outgoing query with the merchant's token attached? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
