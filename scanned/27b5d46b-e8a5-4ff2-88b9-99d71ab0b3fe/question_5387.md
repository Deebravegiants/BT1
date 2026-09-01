# Q5387: initialize — token attached before destination is settled via scheme in path

## Question
Can a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL, supplied by an unprivileged attacker at `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`, make `Clients::HttpClient#initialize` and the code consuming its result disagree, given that `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#initialize`
- Entrypoint: `HttpClient.new(base_path:, session:)`, which sets `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`
- Attacker controls: a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL
- Exploit idea: `X-Shopify-Access-Token` is added in the constructor, before any per-request check of where the URL will resolve
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
