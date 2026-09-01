# Q347: normalize_headers — no allow-list via colliding header names

## Question
Can two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`, supplied by an unprivileged attacker at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, make `HttpUtils.normalize_headers` and the code consuming its result disagree, given that any header the client sends can be normalised onto a name the gem treats as trusted? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: two inbound header names that normalise to the same key, e.g. `X_SHOPIFY_TOPIC` and `X-Shopify-Topic`
- Exploit idea: any header the client sends can be normalised onto a name the gem treats as trusted
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
