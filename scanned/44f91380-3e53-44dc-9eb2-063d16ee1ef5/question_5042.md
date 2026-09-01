# Q5042: serialized_error — string interpolation, not URL joining via query/fragment injection

## Question
Does `Clients::HttpClient#serialized_error` collapse two distinct identities into one when an unprivileged attacker submits a `path` containing `?` or `#`, which truncates or rewrites the intended query at `serialized_error`, which builds an error message from response body and headers? Show that the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/http_client.rb` -> `Clients::HttpClient#serialized_error`
- Entrypoint: `serialized_error`, which builds an error message from response body and headers
- Attacker controls: a `path` containing `?` or `#`, which truncates or rewrites the intended query
- Exploit idea: the URL is built by concatenation, so a crafted `path` changes host, scheme, query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: issue two requests on one `HttpClient` and assert the second does not inherit headers merged by the first
