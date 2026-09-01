# Q1434: post — guard order via traversal to another version

## Question
Is there a reachable state in which an unprivileged attacker, controlling `../<other version>/` segments that move the request to an API version the app did not configure at `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token, makes `Clients::Rest::Admin#post` return a result the caller treats as authenticated, given that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#post`
- Entrypoint: `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token
- Attacker controls: `../<other version>/` segments that move the request to an API version the app did not configure
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
