# Q4907: serialized_error — token attached before destination is settled via shop.dev host

## Question
Can an unprivileged attacker reach `Clients::HttpClient#serialized_error` through `serialized_error`, which builds an error message from response body and headers while supplying a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite, so that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
