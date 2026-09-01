# Q377: client_credentials — response trusted as the shop's via response body

## Question
Is there a reachable state in which an unprivileged attacker, controlling the access-token response body, deserialised by `AccessTokenResponse.from_hash` with no schema policing beyond T::Struct at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, makes `Auth::ClientCredentials.client_credentials` return a result the caller treats as authenticated, given that the returned token is bound to the caller-supplied shop, not to a shop the response proves? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: the access-token response body, deserialised by `AccessTokenResponse.from_hash` with no schema policing beyond T::Struct
- Exploit idea: the returned token is bound to the caller-supplied shop, not to a shop the response proves
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the minted session's `shop` equals the host the token request was actually sent to
