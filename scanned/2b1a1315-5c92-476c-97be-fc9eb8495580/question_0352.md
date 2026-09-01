# Q352: client_credentials — no caller authorisation via validator bypass string

## Question
Does `Auth::ClientCredentials.client_credentials` collapse two distinct identities into one when an unprivileged attacker submits a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain) at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request? Show that the function itself does not verify that the caller is entitled to mint a token for this shop, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain)
- Exploit idea: the function itself does not verify that the caller is entitled to mint a token for this shop
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
