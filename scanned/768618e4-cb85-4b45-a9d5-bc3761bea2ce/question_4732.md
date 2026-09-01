# Q4732: serialized_error — header override ordering via api_host config

## Question
Can an unprivileged attacker reach `Clients::HttpClient#serialized_error` through `serialized_error`, which builds an error message from response body and headers while supplying an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere, so that `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
