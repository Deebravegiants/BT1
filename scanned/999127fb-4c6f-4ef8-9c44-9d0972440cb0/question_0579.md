# Q579: append_first_party_development_headers — header override ordering via shop.dev host

## Question
Trace `Clients::HttpClient#append_first_party_development_headers` from `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev` with a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite: because `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#append_first_party_development_headers`
- Entrypoint: `append_first_party_development_headers`, which rewrites `Host` and `x-forwarded-host` for `.my.shop.dev`
- Attacker controls: a `session.shop` or `Host` header containing `.my.shop.dev`, entering the first-party development header rewrite
- Exploit idea: `extra_headers` is merged last, so a caller-influenced header wins over the security-relevant defaults
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the raised `HttpResponseError` message contains no access token, `client_secret` or `Authorization` value
