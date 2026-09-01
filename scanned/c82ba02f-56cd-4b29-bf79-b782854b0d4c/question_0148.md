# Q148: client_credentials — sanitised value is the only guard via response body

## Question
Starting from `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, can an unprivileged attacker supply the access-token response body, deserialised by `AccessTokenResponse.from_hash` with no schema policing beyond T::Struct so that everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Auth::ClientCredentials.client_credentials`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: the access-token response body, deserialised by `AccessTokenResponse.from_hash` with no schema policing beyond T::Struct
- Exploit idea: everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
