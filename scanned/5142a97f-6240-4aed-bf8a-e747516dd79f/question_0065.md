# Q65: normalize_headers — first-occurrence substitution via underscore-to-dash aliasing

## Question
Does `HttpUtils.normalize_headers` collapse two distinct identities into one when an unprivileged attacker submits a header whose underscores become dashes and thereby impersonate a Shopify header at `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`? Show that `sub` targets the first `http_` anywhere in the name, not a prefix, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header whose underscores become dashes and thereby impersonate a Shopify header
- Exploit idea: `sub` targets the first `http_` anywhere in the name, not a prefix
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a client-supplied `http_x-shopify-*` header cannot normalise onto a header the webhook or proxy path trusts
