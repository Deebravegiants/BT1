# Q302: client_credentials — response trusted as the shop's via shop argument

## Question
Starting from `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, can an unprivileged attacker supply the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host so that the returned token is bound to the caller-supplied shop, not to a shop the response proves? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Auth::ClientCredentials.client_credentials`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: the `shop:` argument, sanitised by `ShopValidator.sanitize!` and then interpolated into the request host
- Exploit idea: the returned token is bound to the caller-supplied shop, not to a shop the response proves
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
