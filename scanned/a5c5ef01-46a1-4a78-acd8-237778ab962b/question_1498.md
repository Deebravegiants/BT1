# Q1498: post — path built by interpolation via query hash injection

## Question
Can an unprivileged attacker reach `Clients::Rest::Admin#post` through `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token while supplying a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query, so that resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#post`
- Entrypoint: `Rest::Admin#post(path:, body:, ...)`, whose `body` is JSON-serialised and sent with the merchant's access token
- Attacker controls: a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query
- Exploit idea: resource ids are concatenated into the path with no escaping, so a crafted id changes the resource or the host
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
