# Q2400: set_property — method shadowing via response-driven attribute names

## Question
Is there a reachable state in which an unprivileged attacker, controlling attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, makes `Rest::Base#set_property` return a result the caller treats as authenticated, given that a property write can shadow or overwrite internal state such as the session or client held on the instance? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: attribute names arriving in API response JSON, which become `public_send("#{attribute}=")` and `instance_variable_set("@#{clean_key}")` targets
- Exploit idea: a property write can shadow or overwrite internal state such as the session or client held on the instance
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
