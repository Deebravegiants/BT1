# Q4902: request_url — host header split from connection host via request.path

## Question
Does `Clients::HttpClient#request_url` collapse two distinct identities into one when an unprivileged attacker submits the `path` on `HttpRequest`, interpolated straight into the URL with no escaping at the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation? Show that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: the `path` on `HttpRequest`, interpolated straight into the URL with no escaping
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
