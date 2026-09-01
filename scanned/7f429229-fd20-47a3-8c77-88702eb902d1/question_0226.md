# Q226: client_credentials — response trusted as the shop's via dev trusted domains

## Question
Does `Auth::ClientCredentials.client_credentials` collapse two distinct identities into one when an unprivileged attacker submits a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request? Show that the returned token is bound to the caller-supplied shop, not to a shop the response proves, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production
- Exploit idea: the returned token is bound to the caller-supplied shop, not to a shop the response proves
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
