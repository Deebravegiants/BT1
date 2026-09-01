# Q96: client_credentials — response trusted as the shop's via validator bypass string

## Question
Trace `Auth::ClientCredentials.client_credentials` from `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request with a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain): because the returned token is bound to the caller-supplied shop, not to a shop the response proves, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain)
- Exploit idea: the returned token is bound to the caller-supplied shop, not to a shop the response proves
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
