# Q1964: trusted_domains — path segment trusted as identity via caller-supplied myshopify_domain

## Question
Can a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call, supplied by an unprivileged attacker at `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only, make `ShopValidator.trusted_domains` and the code consuming its result disagree, given that the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call
- Exploit idea: the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
