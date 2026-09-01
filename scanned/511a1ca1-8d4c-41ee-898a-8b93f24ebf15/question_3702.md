# Q3702: session_id_from_shopify_id_token — interpolation collision via online flag flip

## Question
Is there a reachable state in which an unprivileged attacker, controlling control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, makes `SessionUtils.session_id_from_shopify_id_token` return a result the caller treats as authenticated, given that string concatenation with `_` makes distinct identities collide? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: control of whether the caller passes `online: true` or `false`, selecting between the online and offline key for the same token
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
