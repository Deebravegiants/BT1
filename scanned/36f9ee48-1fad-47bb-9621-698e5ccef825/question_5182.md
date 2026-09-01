# Q5182: append_first_party_development_headers — response content into logs via deprecation header

## Question
Does `Clients::HttpClient#append_first_party_development_headers` collapse two distinct identities into one when an unprivileged attacker submits an `x-shopify-api-deprecated-reason` response header, which is logged verbatim at `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`? Show that response-controlled strings reach `Context.logger` and the exception message alongside request context, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: an `x-shopify-api-deprecated-reason` response header, which is logged verbatim
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
