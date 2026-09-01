# Q3672: current_session_id — fallback weakens the strong path via chosen cookie value

## Question
Can the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check, supplied by an unprivileged attacker at `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves, make `SessionUtils.current_session_id` and the code consuming its result disagree, given that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.current_session_id`
- Entrypoint: `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
