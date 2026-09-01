# Q4098: request_url — string interpolation, not URL joining via request.path

## Question
If an unprivileged attacker submits the `path` on `HttpRequest`, interpolated straight into the URL with no escaping to the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation, does `Clients::HttpClient#request_url` end up acting on a value that was never authenticated, because the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request_url`
- Entrypoint: the protected `request_url`, a bare `"#{@base_uri_and_path}/#{request.path}"` interpolation
- Attacker controls: the `path` on `HttpRequest`, interpolated straight into the URL with no escaping
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
