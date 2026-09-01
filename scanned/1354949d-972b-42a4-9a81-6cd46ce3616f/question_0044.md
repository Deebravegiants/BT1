# Q44: client_credentials — client_secret sent to a derived host via repeated invocation

## Question
Does `Auth::ClientCredentials.client_credentials` collapse two distinct identities into one when an unprivileged attacker submits repeated calls for arbitrary shop names, since nothing binds the call to an authenticated request at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request? Show that the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: repeated calls for arbitrary shop names, since nothing binds the call to an authenticated request
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{validated_shop}/admin/oauth/access_token`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
