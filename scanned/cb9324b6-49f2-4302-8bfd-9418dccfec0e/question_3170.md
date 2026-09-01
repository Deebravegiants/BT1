# Q3170: make_request — caller headers win via path prefix admin/

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, makes `Clients::Rest::Admin#make_request` return a result the caller treats as authenticated, given that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
