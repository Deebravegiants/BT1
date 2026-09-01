# Q5525: get_path — template selection is textual via pagination cursors

## Question
Does `Rest::Base.get_path` collapse two distinct identities into one when an unprivileged attacker submits `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request at `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids? Show that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
