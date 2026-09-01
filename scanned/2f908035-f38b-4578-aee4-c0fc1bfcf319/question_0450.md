# Q450: client_credentials — client_secret sent to a derived host via dev trusted domains

## Question
Does `Auth::ClientCredentials.client_credentials` collapse two distinct identities into one when an unprivileged attacker submits a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request? Show that the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
