# Q3058: jwt_session_id — fallback weakens the strong path via cookie plus token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a request presenting both a cookie and an id token with conflicting shops at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, makes `SessionUtils.jwt_session_id` return a result the caller treats as authenticated, given that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
