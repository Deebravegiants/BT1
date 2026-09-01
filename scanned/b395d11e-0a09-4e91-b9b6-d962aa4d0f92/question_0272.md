# Q272: normalize_headers — collision resolved by ordering via attacker-added prefix

## Question
Is there a reachable state in which an unprivileged attacker, controlling a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, makes `HttpUtils.normalize_headers` return a result the caller treats as authenticated, given that the surviving value depends on hash insertion order, which the request controls? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key
- Exploit idea: the surviving value depends on hash insertion order, which the request controls
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: pass a hash with two colliding names and assert which value survives, then assert the surviving value cannot be attacker-chosen
