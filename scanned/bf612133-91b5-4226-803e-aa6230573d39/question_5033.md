# Q5033: base_find — cursor trusted via pagination cursors

## Question
Can an unprivileged attacker reach `Rest::Base.base_find` through `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params` while supplying `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request, so that page-info cursors from a response are replayed into the next authenticated request without validation, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.base_find`
- Entrypoint: `base_find(session:, ids:, params:)`, called by every generated `find`/`all` with caller-supplied `ids` and `params`
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: page-info cursors from a response are replayed into the next authenticated request without validation
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
