# Q2334: request_url — prefix re-rooting via body-type coupling

## Question
If an unprivileged attacker submits a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify` to the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`, does `Clients::Rest::Admin#request_url` end up acting on a value that was never authenticated, because the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#request_url`
- Entrypoint: the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`
- Attacker controls: a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify`
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
