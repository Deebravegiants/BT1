# Q469: normalize_headers — first-occurrence substitution via colliding header names

## Question
Can an unprivileged attacker reach `HttpUtils.normalize_headers` through `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")` while supplying two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`, so that `sub` targets the first `http_` anywhere in the name, not a prefix, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`
- Exploit idea: `sub` targets the first `http_` anywhere in the name, not a prefix
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
