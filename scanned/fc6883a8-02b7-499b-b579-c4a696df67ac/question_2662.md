# Q2662: request_url — attacker-steered retry loop via api_host config

## Question
Does `Clients::HttpClient#request_url` collapse two distinct identities into one when an unprivileged attacker submits an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation? Show that response headers decide how long and how often the authenticated request is repeated, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: an `api_host` configured so `Host` is set from `session.shop` while the connection goes elsewhere
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
