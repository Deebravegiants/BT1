# Q5212: request — dev-mode rewrite in production via request.path

## Question
Can the `path` on `HttpRequest`, interpolated straight into the URL with no escaping, supplied by an unprivileged attacker at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request, make `Clients::HttpClient#request` and the code consuming its result disagree, given that the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: the `path` on `HttpRequest`, interpolated straight into the URL with no escaping
- Exploit idea: the `DevServer` branch fires whenever the constant happens to be defined, rewriting `Host` for `.my.shop.dev`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
