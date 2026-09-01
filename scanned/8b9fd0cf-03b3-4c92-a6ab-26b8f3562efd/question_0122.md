# Q122: client_credentials — no caller authorisation via dev trusted domains

## Question
If an unprivileged attacker submits a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production to `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, does `Auth::ClientCredentials.client_credentials` end up acting on a value that was never authenticated, because the function itself does not verify that the caller is entitled to mint a token for this shop? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a `spin.dev` or `shop.dev` host, both present in `TRUSTED_SHOPIFY_DOMAINS` in production
- Exploit idea: the function itself does not verify that the caller is entitled to mint a token for this shop
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
