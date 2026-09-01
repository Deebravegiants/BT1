# Q4702: request_url — host header split from connection host via query/fragment injection

## Question
Trace `Clients::HttpClient#request_url` from the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation with a `path` containing `?` or `#`, which truncates or rewrites the intended query: because when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: a `path` containing `?` or `#`, which truncates or rewrites the intended query
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
