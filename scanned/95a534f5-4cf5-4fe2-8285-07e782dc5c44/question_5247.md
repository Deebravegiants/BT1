# Q5247: serialized_error — string interpolation, not URL joining via session.shop

## Question
Can `session.shop`, which for several flows was never passed through `ShopValidator`, supplied by an unprivileged attacker at `serialized_error`, which builds an error message from response body and headers, make `Clients::HttpClient#serialized_error` and the code consuming its result disagree, given that the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: `session.shop`, which for several flows was never passed through `ShopValidator`
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
