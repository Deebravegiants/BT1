# Q5484: serialized_error — response content into logs via base_path argument

## Question
If an unprivileged attacker submits the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation to `serialized_error`, which builds an error message from response body and headers, does `Clients::HttpClient#serialized_error` end up acting on a value that was never authenticated, because response-controlled strings reach `Context.logger` and the exception message alongside request context? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation
- Exploit idea: response-controlled strings reach `Context.logger` and the exception message alongside request context
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: issue a request with a crafted `path` and assert the recorded request URI's host equals `session.shop`
