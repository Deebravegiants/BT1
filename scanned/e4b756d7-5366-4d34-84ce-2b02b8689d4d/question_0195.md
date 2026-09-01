# Q195: normalize_headers — collision resolved by ordering via ordering dependence

## Question
Is there a reachable state in which an unprivileged attacker, controlling control over the order in which colliding headers appear, deciding which value survives the `to_h` rebuild at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, makes `HttpUtils.normalize_headers` return a result the caller treats as authenticated, given that the surviving value depends on hash insertion order, which the request controls? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: control over the order in which colliding headers appear, deciding which value survives the `to_h` rebuild
- Exploit idea: the surviving value depends on hash insertion order, which the request controls
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
