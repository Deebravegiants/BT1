# Q297: normalize_headers — lossy normalisation via attacker-added prefix

## Question
If an unprivileged attacker submits a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key to `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, does `HttpUtils.normalize_headers` end up acting on a value that was never authenticated, because the rewrite is not injective, so distinct inbound headers become one key and one silently wins? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key
- Exploit idea: the rewrite is not injective, so distinct inbound headers become one key and one silently wins
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
