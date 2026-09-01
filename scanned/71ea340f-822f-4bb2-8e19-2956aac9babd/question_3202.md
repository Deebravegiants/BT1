# Q3202: serialized_error — mutable shared header hash via shop.dev host

## Question
If an unprivileged attacker submits a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite to `serialized_error`, which builds an error message from response body and headers, does `Clients::HttpClient#serialized_error` end up acting on a value that was never authenticated, because `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite
- Exploit idea: `headers = @headers` aliases the instance hash, so per-request mutations persist across requests on the same client
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
