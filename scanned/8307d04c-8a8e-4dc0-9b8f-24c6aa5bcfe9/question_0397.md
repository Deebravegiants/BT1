# Q397: normalize_headers — lossy normalisation via colliding header names

## Question
Trace `HttpUtils.normalize_headers` from `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")` with two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`: because the rewrite is not injective, so distinct inbound headers become one key and one silently wins, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`
- Exploit idea: the rewrite is not injective, so distinct inbound headers become one key and one silently wins
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
