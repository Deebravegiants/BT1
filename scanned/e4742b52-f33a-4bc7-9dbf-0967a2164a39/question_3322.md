# Q3322: offline_session_id — caller decides identity shape via online flag flip

## Question
Can control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token, supplied by an unprivileged attacker at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, make `SessionUtils.offline_session_id` and the code consuming its result disagree, given that the `online` boolean, not the token, selects which identity is loaded? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
