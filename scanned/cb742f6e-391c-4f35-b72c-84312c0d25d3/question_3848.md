# Q3848: trusted_domains — normalisation happens after the decision via embedded port

## Question
Trace `ShopValidator.trusted_domains` from `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only with a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`: because the value returned is `uri.host`, not the fully normalised string the caller later interpolates, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.trusted_domains`
- Entrypoint: `trusted_domains`, which appends the caller-supplied `myshopify_domain:` keyword to `TRUSTED_SHOPIFY_DOMAINS` for that call only
- Attacker controls: a shop string carrying an explicit port such as `victim.myshopify.com:8443` or `myshopify.com:80@evil.example`
- Exploit idea: the value returned is `uri.host`, not the fully normalised string the caller later interpolates
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
