# Q2628: get_path — query forwarded verbatim via response-driven attribute names

## Question
If an unprivileged attacker submits attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets to `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids, does `Rest::Base.get_path` end up acting on a value that was never authenticated, because `params:` is passed through to the outgoing query with the merchant's token attached? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path`
- Entrypoint: `Rest::Base.get_path(http_method:, operation:, entity:, ids:)`, which matches a path template and interpolates ids
- Attacker controls: attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets
- Exploit idea: `params:` is passed through to the outgoing query with the merchant's token attached
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
