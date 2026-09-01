# Q4983: get_path — path interpolation from ids via original_state diff

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends at `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids, makes `Rest::Base.get_path` return a result the caller treats as authenticated, given that ids are concatenated into the path template with no escaping or type check? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: the `original_state` snapshot that `attributes_to_update` diffs against, deciding which fields a `PUT` actually sends
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
