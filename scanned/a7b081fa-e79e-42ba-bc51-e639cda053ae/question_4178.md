# Q4178: offline_session_id — caller decides identity shape via cookie plus token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a request presenting both a cookie and an id token with conflicting shops at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, makes `SessionUtils.offline_session_id` return a result the caller treats as authenticated, given that the `online` boolean, not the token, selects which identity is loaded? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
