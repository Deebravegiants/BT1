# Q322: normalize_headers — lossy normalisation via underscore-to-dash aliasing

## Question
Can an unprivileged attacker reach `HttpUtils.normalize_headers` through `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")` while supplying a header whose underscores become dashes and thereby impersonate a Shopify header, so that the rewrite is not injective, so distinct inbound headers become one key and one silently wins, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header whose underscores become dashes and thereby impersonate a Shopify header
- Exploit idea: the rewrite is not injective, so distinct inbound headers become one key and one silently wins
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: pass a hash with two colliding names and assert which value survives, then assert the surviving value cannot be attacker-chosen
