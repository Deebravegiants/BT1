# Q4172: get_path_ids — read-only filter applied late via pagination cursors

## Question
Can an unprivileged attacker reach `Rest::Base.get_path_ids` through `get_path_ids`, which enumerates the id placeholders a path template requires while supplying `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request, so that the read-only filter runs at serialisation time, after values have already been set on the instance, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: `prev_page_info` / `next_page_info` values taken from response `Link` headers and replayed into a subsequent request
- Exploit idea: the read-only filter runs at serialisation time, after values have already been set on the instance
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
