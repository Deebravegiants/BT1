# Q3722: current_session_id — caller decides identity shape via online flag flip

## Question
Trace `SessionUtils.current_session_id` from `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves with control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token: because the `online` boolean, not the token, selects which identity is loaded, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.current_session_id`
- Entrypoint: `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
