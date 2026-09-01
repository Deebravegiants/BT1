# Q4538: request — string interpolation, not URL joining via base_path argument

## Question
Does `Clients::HttpClient#request` collapse two distinct identities into one when an unprivileged attacker submits the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation at `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request? Show that the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#request`
- Entrypoint: `HttpClient#request(request, response_as_struct:)`, the single outbound call site for every REST and GraphQL request
- Attacker controls: the `base_path:` argument, concatenated into `@base_uri_and_path` with no separator normalisation
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
