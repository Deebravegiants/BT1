# Q277: client_credentials — client_secret sent to a derived host via shop argument

## Question
Can the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host, supplied by an unprivileged attacker at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, make `Auth::ClientCredentials.client_credentials` and the code consuming its result disagree, given that the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the minted session's `shop` equals the host the token request was actually sent to
