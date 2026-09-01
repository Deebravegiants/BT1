# Q3642: serialized_error — token attached before destination is settled via deprecation header

## Question
Does `Clients::HttpClient#serialized_error` collapse two distinct identities into one when an unprivileged attacker submits an `x-shopify-api-deprecated-reason` response header, which is logged verbatim at `serialized_error`, which builds an error message from response body and headers? Show that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: an `x-shopify-api-deprecated-reason` response header, which is logged verbatim
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
