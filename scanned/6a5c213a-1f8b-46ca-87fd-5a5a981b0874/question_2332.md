# Q2332: jwt_session_id — no shop cross-check via chosen cookie value

## Question
Starting from `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, can an unprivileged attacker supply the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check so that nothing asserts the loaded session's `shop` matches the shop authenticated by this request? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `SessionUtils.jwt_session_id`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
