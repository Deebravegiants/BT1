# Q5084: unified_admin? — validated value discarded via caller-supplied myshopify_domain

## Question
Does `ShopValidator.unified_admin?` collapse two distinct identities into one when an unprivileged attacker submits a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call at the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`? Show that the caller validates one string but interpolates a different, unvalidated one into the URL or the session id, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.unified_admin?`
- Entrypoint: the unified-admin branch, entered whenever the first label of the parsed host is literally `admin`
- Attacker controls: a request that reaches a code path where `myshopify_domain:` is derived from user input, widening `trusted_domains` for that call
- Exploit idea: the caller validates one string but interpolates a different, unvalidated one into the URL or the session id
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
