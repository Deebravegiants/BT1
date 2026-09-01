# Q3380: set_property — path interpolation from ids via has_many element class

## Question
Is there a reachable state in which an unprivileged attacker, controlling the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated at `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data, makes `Rest::Base#set_property` return a result the caller treats as authenticated, given that ids are concatenated into the path template with no escaping or type check? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base#set_property`
- Entrypoint: `set_property(key, val)`, which performs `instance_variable_set("@#{clean_key}", val)` with a key taken from response data
- Attacker controls: the element class resolved for a `has_many` attribute from response data, which decides how nested payloads are instantiated
- Exploit idea: ids are concatenated into the path template with no escaping or type check
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `params:` values are query-escaped in the recorded request and cannot introduce a second query or a fragment
