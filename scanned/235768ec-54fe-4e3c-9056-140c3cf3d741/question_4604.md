# Q4604: request — string interpolation, not URL joining via error body content

## Question
Trace `Clients::HttpClient#request` from `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request with a response body whose `errors`/`error_description` fields are echoed into the raised exception message: because the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: a response body whose `errors`/`error_description` fields are echoed into the raised exception message
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
