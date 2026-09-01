# Q3507: hmac — verified bytes != parsed bytes via underscore/dash aliasing

## Question
Can an unprivileged attacker reach `Webhooks::Request#hmac` through `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header while supplying header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`, so that `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#hmac`
- Entrypoint: `Request#hmac`, which returns `Digest.hexencode(Base64.decode64(header))` for the `x-shopify-hmac-sha256` header
- Attacker controls: header names that collide after `downcase.sub("http_","").gsub("_","-")`, e.g. `HTTP_X_SHOPIFY_TOPIC` vs `X-Shopify-Topic`
- Exploit idea: `@raw_body` at verification time and the string `JSON.parse` consumes are not guaranteed identical
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
