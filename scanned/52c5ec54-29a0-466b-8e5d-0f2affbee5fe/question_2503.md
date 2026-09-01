# Q2503: make_request — prefix re-rooting via query hash injection

## Question
Can a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query, supplied by an unprivileged attacker at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, make `Clients::Rest::Admin#make_request` and the code consuming its result disagree, given that the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
