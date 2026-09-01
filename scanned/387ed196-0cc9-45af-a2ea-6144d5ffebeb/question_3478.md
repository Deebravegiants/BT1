# Q3478: make_request — rewrite is textual via query hash injection

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, makes `Clients::Rest::Admin#make_request` return a result the caller treats as authenticated, given that the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
