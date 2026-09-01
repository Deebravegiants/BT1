# Q711: initialize — host header split from connection host via extra_headers

## Question
Can `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`, supplied by an unprivileged attacker at `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`, make `Clients::HttpClient#initialize` and the code consuming its result disagree, given that when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: `extra_headers` merged after the base headers, able to override `X-Shopify-Access-Token`, `Host` or `Content-Type`
- Exploit idea: when `api_host` is set, `Host` is `session.shop` while the socket goes to `api_host`, so the two identities diverge
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
