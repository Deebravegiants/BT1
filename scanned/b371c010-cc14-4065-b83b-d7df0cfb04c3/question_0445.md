# Q445: normalize_headers — collision resolved by ordering via http_ inside a name

## Question
Can a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere, supplied by an unprivileged attacker at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, make `HttpUtils.normalize_headers` and the code consuming its result disagree, given that the surviving value depends on hash insertion order, which the request controls? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere
- Exploit idea: the surviving value depends on hash insertion order, which the request controls
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
