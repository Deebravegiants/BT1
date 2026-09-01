# Q498: client_credentials — sanitised value is the only guard via dev trusted domains

## Question
Starting from `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, can an unprivileged attacker supply a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production so that everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Auth::ClientCredentials.client_credentials`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production
- Exploit idea: everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
