# Q3674: get — rewrite is textual via double .json

## Question
Is there a reachable state in which an unprivileged attacker, controlling a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite at `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, makes `Clients::Rest::Admin#get` return a result the caller treats as authenticated, given that the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
