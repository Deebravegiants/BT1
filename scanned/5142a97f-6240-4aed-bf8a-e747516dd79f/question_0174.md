# Q174: client_credentials — sanitised value is the only guard via shop argument

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, makes `Auth::ClientCredentials.client_credentials` return a result the caller treats as authenticated, given that everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host
- Exploit idea: everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
