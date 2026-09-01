# Q143: normalize_headers — no allow-list via attacker-added prefix

## Question
If an unprivileged attacker submits a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key to `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, does `HttpUtils.normalize_headers` end up acting on a value that was never authenticated, because any header the client sends can be normalised onto a name the gem treats as trusted? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header the attacker names `http_x-shopify-hmac-sha256` so it normalises onto a security-relevant key
- Exploit idea: any header the client sends can be normalised onto a name the gem treats as trusted
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
