# Q372: normalize_headers — no allow-list via http_ inside a name

## Question
Starting from `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`, can an unprivileged attacker supply a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere so that any header the client sends can be normalised onto a name the gem treats as trusted? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `HttpUtils.normalize_headers`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/http_utils.rb` -> `HttpUtils.normalize_headers`
- Entrypoint: `ShopifyAPI::Utils::HttpUtils.normalize_headers`, which rewrites every key with `downcase.sub("http_","").gsub("_","-")`
- Attacker controls: a header name containing `http_` other than as a prefix, since `sub` replaces the first occurrence anywhere
- Exploit idea: any header the client sends can be normalised onto a name the gem treats as trusted
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: pass a hash with two colliding names and assert which value survives, then assert the surviving value cannot be attacker-chosen
