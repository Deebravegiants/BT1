# Q2878: serialized_error — attacker-steered retry loop via scheme in path

## Question
Starting from `serialized_error`, which builds an error message from response body and headers, can an unprivileged attacker supply a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL so that response headers decide how long and how often the authenticated request is repeated? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Clients::HttpClient#serialized_error`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `path` containing `https://` or an encoded scheme, turning the interpolation into an absolute URL
- Exploit idea: response headers decide how long and how often the authenticated request is repeated
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
