# Q247: normalize_headers — first-occurrence substitution via attacker-added prefix

## Question
Does `HttpUtils.normalize_headers` collapse two distinct identities into one when an unprivileged attacker submits a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`? Show that `sub` targets the first `http_` anywhere in the name, not a prefix, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key
- Exploit idea: `sub` targets the first `http_` anywhere in the name, not a prefix
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
