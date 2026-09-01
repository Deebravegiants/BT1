# Q2270: get_path_ids — path interpolation from ids via pagination cursors

## Question
Does `Rest::Base.get_path_ids` collapse two distinct identities into one when an unprivileged attacker submits `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request at `get_path_ids`, which enumerates the id placeholders a path template requires? Show that ids are concatenated into the path template with no escaping or type check, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
