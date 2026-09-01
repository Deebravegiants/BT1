# Q5551: to_signable_string — lossy digest normalisation via duplicate header prefixes

## Question
Can an unprivileged attacker reach `Webhooks::Request#to_signable_string` through `to_signable_string`, which returns `@raw_body` and nothing else while supplying both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order, so that `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/webhooks/request.rb` -> `Webhooks::Request#to_signable_string`
- Entrypoint: `to_signable_string`, which returns `@raw_body` and nothing else
- Attacker controls: both `shopify-topic` and `x-shopify-topic` set to different values, exploiting the `||` preference order
- Exploit idea: `Base64.decode64` is permissive, so many distinct header values collapse to the same compared digest
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: register two handlers, replay one signed body under each topic header, and assert only the signed topic is dispatched
