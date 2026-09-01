# Q1818: post — prefix re-rooting via traversal to another version

## Question
Trace `Clients::Rest::Admin#post` from `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token with `../<other version>/` segments that move the request to an API version the app did not configure: because the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#post`
- Entrypoint: `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token
- Attacker controls: `../<other version>/` segments that move the request to an API version the app did not configure
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
