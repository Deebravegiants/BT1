# Q13: normalize_headers — collision resolved by ordering via underscore-to-dash aliasing

## Question
Is there a reachable state in which an unprivileged attacker, controlling a header whose underscores become dashes and thereby impersonate a Shopify header at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, makes `HttpUtils.normalize_headers` return a result the caller treats as authenticated, given that the surviving value depends on hash insertion order, which the request controls? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header whose underscores become dashes and thereby impersonate a Shopify header
- Exploit idea: the surviving value depends on hash insertion order, which the request controls
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
