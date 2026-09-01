# Q39: normalize_headers — first-occurrence substitution via http_ inside a name

## Question
Can a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere, supplied by an unprivileged attacker at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, make `HttpUtils.normalize_headers` and the code consuming its result disagree, given that `sub` targets the first `http_` anywhere in the name, not a prefix? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere
- Exploit idea: `sub` targets the first `http_` anywhere in the name, not a prefix
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
