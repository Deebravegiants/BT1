# Q426: client_credentials — response trusted as the shop's via repeated invocation

## Question
Is there a reachable state in which an unprivileged attacker, controlling repeated calls for arbitrary shop names, since nothing binds the call to an authenticated request at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, makes `Auth::ClientCredentials.client_credentials` return a result the caller treats as authenticated, given that the returned token is bound to the caller-supplied shop, not to a shop the response proves? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: repeated calls for arbitrary shop names, since nothing binds the call to an authenticated request
- Exploit idea: the returned token is bound to the caller-supplied shop, not to a shop the response proves
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
